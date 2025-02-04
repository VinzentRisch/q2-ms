from qiime2.plugin.testing import TestPluginBase

from q2_ms.xcms.filter_features import validate_parameters


class TestValidateFilterParameters(TestPluginBase):
    package = "q2_ms.xcms.tests"

    def test_invalid_percent_missing_filter(self):
        with self.assertRaisesRegex(
            ValueError,
            "The parameter 'qc_index' cannot be used in combination with the filter "
            "'percent-missing'",
        ):
            validate_parameters(
                filter="percent-missing", threshold=30, qc_index="some_index"
            )
