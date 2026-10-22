import os
import subprocess

def test_build():
    cwd = r"d:\file_save\workspace\github\weekly-mountain"
    res = subprocess.run(
        "npm run build",
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    assert res.returncode == 0, f"Build failed: {res.stderr}\n{res.stdout}"
    dist_html = os.path.join(cwd, "dist", "index.html")
    assert os.path.exists(dist_html), "dist/index.html missing"
    with open(dist_html, "r", encoding="utf-8") as f:
        content = f.read()
    # 验证不含根绝对路径资源
    assert 'src="/assets/' not in content and 'href="/assets/' not in content, "Absolute /assets path found!"
    assert ('src="./assets/' in content or 'href="./assets/' in content or
            'src="assets/' in content or 'href="assets/' in content), "Relative asset path not found in dist/index.html"
    print("PASS: Vite build succeeded with relative asset paths")

if __name__ == "__main__":
    test_build()
