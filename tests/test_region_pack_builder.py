import hashlib
import json
import os
import unittest
import zipfile

FORBIDDEN_KEYWORD = chr(0x5b98) + chr(0x65b9)


def calculate_sha256(filepath):
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


class TestRegionPackBuilder(unittest.TestCase):
    def setUp(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.dist_packs_dir = os.path.join(self.project_root, "dist-packs")
        self.regions_json_path = os.path.join(
            self.project_root, "src", "data", "regions.json"
        )
        self.cd_pack_path = os.path.join(
            self.dist_packs_dir, "pack-chengdu-v1.0.0.zip"
        )
        self.cq_pack_path = os.path.join(
            self.dist_packs_dir, "pack-chongqing-v1.0.0.zip"
        )
        self.build_script_path = os.path.join(
            self.project_root, "scripts", "build_region_packs.py"
        )

    def test_packs_exist(self):
        """验证 dist-packs 下两份离线资源包均存在"""
        self.assertTrue(
            os.path.exists(self.cd_pack_path),
            f"成都离线包未生成: {self.cd_pack_path}",
        )
        self.assertTrue(
            os.path.exists(self.cq_pack_path),
            f"重庆离线包未生成: {self.cq_pack_path}",
        )

    def test_chengdu_pack_integrity(self):
        """验证成都离线包内文件、数据量及违规词"""
        self.assertTrue(os.path.exists(self.cd_pack_path))
        with zipfile.ZipFile(self.cd_pack_path, "r") as z:
            namelist = z.namelist()
            self.assertIn("mountains.json", namelist, "成都包根目录缺少 mountains.json")

            for name in namelist:
                if name.endswith((".json", ".txt", ".md", ".geojson")):
                    content = z.read(name).decode("utf-8")
                    self.assertNotIn(
                        FORBIDDEN_KEYWORD,
                        content,
                        f"成都包内文件 {name} 包含违规词",
                    )

            cd_content = z.read("mountains.json").decode("utf-8")
            cd_data = json.loads(cd_content)
            self.assertEqual(len(cd_data), 51, "成都山峰数量必须为 51")
            ids = [m["id"] for m in cd_data]
            self.assertEqual(len(ids), len(set(ids)), "成都山峰 ID 必须全局唯一")

    def test_chongqing_pack_integrity(self):
        """验证重庆离线包内文件、数据量及违规词"""
        self.assertTrue(os.path.exists(self.cq_pack_path))
        with zipfile.ZipFile(self.cq_pack_path, "r") as z:
            namelist = z.namelist()
            self.assertIn("mountains.json", namelist, "重庆包根目录缺少 mountains.json")

            for name in namelist:
                if name.endswith((".json", ".txt", ".md", ".geojson")):
                    content = z.read(name).decode("utf-8")
                    self.assertNotIn(
                        FORBIDDEN_KEYWORD,
                        content,
                        f"重庆包内文件 {name} 包含违规词",
                    )

            cq_content = z.read("mountains.json").decode("utf-8")
            cq_data = json.loads(cq_content)
            self.assertEqual(len(cq_data), 36, "重庆山峰数量必须为 36")
            ids = [m["id"] for m in cq_data]
            self.assertEqual(len(ids), len(set(ids)), "重庆山峰 ID 必须全局唯一")

    def test_regions_json_pack_info_synced(self):
        """验证 regions.json 中 packInfo 的 sizeBytes 与 sha256 与构建包严格一致"""
        self.assertTrue(os.path.exists(self.regions_json_path))
        self.assertTrue(os.path.exists(self.cd_pack_path))
        self.assertTrue(os.path.exists(self.cq_pack_path))

        with open(self.regions_json_path, "r", encoding="utf-8") as f:
            regions = json.load(f)

        region_map = {r["id"]: r for r in regions}

        # 成都包校验
        cd_info = region_map["chengdu"]["packInfo"]
        expected_cd_size = os.path.getsize(self.cd_pack_path)
        expected_cd_sha = calculate_sha256(self.cd_pack_path)

        self.assertGreater(cd_info["sizeBytes"], 0)
        self.assertEqual(cd_info["sizeBytes"], expected_cd_size)
        self.assertEqual(cd_info["sha256"], expected_cd_sha)

        # 重庆包校验
        cq_info = region_map["chongqing"]["packInfo"]
        expected_cq_size = os.path.getsize(self.cq_pack_path)
        expected_cq_sha = calculate_sha256(self.cq_pack_path)

        self.assertGreater(cq_info["sizeBytes"], 0)
        self.assertEqual(cq_info["sizeBytes"], expected_cq_size)
        self.assertEqual(cq_info["sha256"], expected_cq_sha)

    def test_build_script_cleanliness(self):
        """验证构建脚本自身不包含违规词"""
        self.assertTrue(
            os.path.exists(self.build_script_path),
            f"缺少构建脚本: {self.build_script_path}",
        )
        with open(self.build_script_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn(
            FORBIDDEN_KEYWORD,
            content,
            f"构建脚本中发现违规词",
        )


if __name__ == "__main__":
    unittest.main()
