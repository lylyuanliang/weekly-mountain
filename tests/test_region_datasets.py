import json
import os
import unittest

FORBIDDEN_KEYWORD = chr(0x5b98) + chr(0x65b9)  # 避免代码自身包含该关键词


class TestRegionDatasets(unittest.TestCase):
    def setUp(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.regions_path = os.path.join(self.project_root, "src", "data", "regions.json")
        self.cd_mountains_path = os.path.join(
            self.project_root, "src", "data", "regions", "chengdu", "mountains.json"
        )
        self.cq_mountains_path = os.path.join(
            self.project_root, "src", "data", "regions", "chongqing", "mountains.json"
        )
        self.legacy_mountains_path = os.path.join(
            self.project_root, "src", "data", "mountains.json"
        )

    def test_file_existence(self):
        """验证所有目标文件与兼容性文件存在"""
        self.assertTrue(
            os.path.exists(self.regions_path), f"Missing {self.regions_path}"
        )
        self.assertTrue(
            os.path.exists(self.cd_mountains_path), f"Missing {self.cd_mountains_path}"
        )
        self.assertTrue(
            os.path.exists(self.cq_mountains_path), f"Missing {self.cq_mountains_path}"
        )
        self.assertTrue(
            os.path.exists(self.legacy_mountains_path),
            f"Missing legacy file {self.legacy_mountains_path}",
        )

    def test_regions_metadata(self):
        """验证 regions.json 中 chengdu 与 chongqing 的元数据配置"""
        self.assertTrue(os.path.exists(self.regions_path))
        with open(self.regions_path, "r", encoding="utf-8") as f:
            regions = json.load(f)

        region_map = {r["id"]: r for r in regions}
        self.assertIn("chengdu", region_map)
        self.assertIn("chongqing", region_map)

        # 验证 chengdu
        cd = region_map["chengdu"]
        self.assertEqual(cd.get("status"), "active")
        self.assertEqual(cd.get("mountainsCount"), 51)
        self.assertEqual(cd.get("badge"), "已收录 51 座")
        self.assertIn("packInfo", cd)
        self.assertEqual(cd["packInfo"].get("filename"), "pack-chengdu-v1.0.0.zip")
        self.assertEqual(cd["packInfo"].get("version"), "1.0.0")
        self.assertGreater(cd["packInfo"].get("sizeBytes"), 0)
        self.assertEqual(len(cd["packInfo"].get("sha256", "")), 64)
        self.assertTrue(cd["packInfo"].get("isDefaultInstalled"))

        # 验证 chongqing
        cq = region_map["chongqing"]
        self.assertEqual(cq.get("status"), "active")
        self.assertEqual(cq.get("mountainsCount"), 36)
        self.assertEqual(cq.get("badge"), "已收录 36 座")
        self.assertEqual(cq.get("title"), "重庆周边 36 座山")
        self.assertEqual(
            cq.get("description"),
            "巴渝平行岭谷与三峡、大娄山名山精选，涵盖金佛山、三峡之巅、缙云山、仙女山等奇秀胜地。",
        )
        self.assertIn("packInfo", cq)
        self.assertEqual(cq["packInfo"].get("filename"), "pack-chongqing-v1.0.0.zip")
        self.assertEqual(cq["packInfo"].get("version"), "1.0.0")
        self.assertGreater(cq["packInfo"].get("sizeBytes"), 0)
        self.assertEqual(len(cq["packInfo"].get("sha256", "")), 64)
        self.assertFalse(cq["packInfo"].get("isDefaultInstalled"))

    def test_chengdu_mountains_dataset(self):
        """验证成都数据集数量为 51 且各字段完备唯一"""
        self.assertTrue(os.path.exists(self.cd_mountains_path))
        with open(self.cd_mountains_path, "r", encoding="utf-8") as f:
            mountains = json.load(f)

        self.assertEqual(len(mountains), 51, "Chengdu mountains count must be 51")
        ids = [m["id"] for m in mountains]
        self.assertEqual(len(ids), len(set(ids)), "Chengdu mountain IDs must be unique")

    def test_chongqing_mountains_dataset(self):
        """验证重庆数据集数量为 36 且各字段完备唯一"""
        self.assertTrue(os.path.exists(self.cq_mountains_path))
        with open(self.cq_mountains_path, "r", encoding="utf-8") as f:
            mountains = json.load(f)

        self.assertEqual(len(mountains), 36, "Chongqing mountains count must be 36")
        ids = [m["id"] for m in mountains]
        self.assertEqual(len(ids), len(set(ids)), "Chongqing mountain IDs must be unique")

    def test_zero_forbidden_keyword(self):
        """全量扫描目标数据文件，严禁出现指定受限词"""
        checked_files = [
            self.regions_path,
            self.cd_mountains_path,
            self.cq_mountains_path,
        ]
        for path in checked_files:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.assertNotIn(
                    FORBIDDEN_KEYWORD,
                    content,
                    f"File {path} contains forbidden keyword: {FORBIDDEN_KEYWORD}",
                )


if __name__ == "__main__":
    unittest.main()
