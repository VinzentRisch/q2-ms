import os
import shutil

from qiime2.plugin.testing import TestPluginBase

from q2_ms.xcms.utils import change_data_paths, create_fake_mzml_files


class TestXCMSUtils(TestPluginBase):
    package = "q2_ms.xcms.tests"

    def test_change_paths(self):
        tmp = self.temp_dir.name
        shutil.copy(self.get_data_path("change_paths/ms_backend_data.txt"), tmp)
        shutil.copy(
            self.get_data_path("change_paths/ms_experiment_sample_data.txt"), tmp
        )

        change_data_paths(dir_path=tmp, new_directory="test")

        with (
            open(os.path.join(tmp, "ms_backend_data.txt"), "r", encoding="utf-8") as f1,
            open(
                self.get_data_path("change_paths/ms_backend_data_changed.txt"),
                "r",
                encoding="utf-8",
            ) as f2,
        ):
            self.assertTrue(f1.read() == f2.read())

        with (
            open(
                os.path.join(tmp, "ms_experiment_sample_data.txt"),
                "r",
                encoding="utf-8",
            ) as f1,
            open(
                self.get_data_path(
                    "change_paths/ms_experiment_sample_data_changed.txt"
                ),
                "r",
                encoding="utf-8",
            ) as f2,
        ):
            self.assertTrue(f1.read() == f2.read())

    def test_create_fake_mzml_files(self):
        xcms_experiment_path = self.get_data_path("change_paths")
        create_fake_mzml_files(xcms_experiment_path)
        self.assertTrue(
            os.path.exists(
                "/private/var/folders/nj/rfpdzc_90zl3555cttz236_w0000gp/T/qiime2/"
                "rischv/data/d1f25fbd-f167-409d-9e42-f46dc3445d32/data/KO/ko15.CDF"
            )
        )
        self.assertTrue(
            os.path.exists(
                "/private/var/folders/nj/rfpdzc_90zl3555cttz236_w0000gp/T/qiime2/"
                "rischv/data/d1f25fbd-f167-409d-9e42-f46dc3445d32/data/KO/ko16.CDF"
            )
        )
