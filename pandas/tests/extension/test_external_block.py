import numpy as np
import pytest

import pandas as pd
from pandas.core.internals import BlockManager
from pandas.core.internals.blocks import ExtensionBlock


class CustomBlock(ExtensionBlock):

    _holder = np.ndarray
    _can_hold_na = False

    def concat_same_type(self, to_concat, placement=None):
        """
        Always concatenate disregarding self.ndim as the values are
        always 1D in this custom Block
        """
        values = np.concatenate([blk.values for blk in to_concat])
        return self.make_block_same_class(
            values, placement=placement or slice(0, len(values), 1)
        )


@pytest.fixture
def df():
    df1 = pd.DataFrame({"a": [1, 2, 3]})
    blocks = df1._data.blocks
    values = np.arange(3, dtype="int64")
    custom_block = CustomBlock(values, placement=slice(1, 2))
    blocks = blocks + (custom_block,)
    block_manager = BlockManager(blocks, [pd.Index(["a", "b"]), df1.index])
    return pd.DataFrame(block_manager)


def test_concat_dataframe(df):
    # GH17728
    res = pd.concat([df, df])
    assert isinstance(res._data.blocks[1], CustomBlock)


def test_concat_axis1(df):
    # GH17954
    df2 = pd.DataFrame({"c": [0.1, 0.2, 0.3]})
    res = pd.concat([df, df2], axis=1)
    assert isinstance(res._data.blocks[1], CustomBlock)
