#!/usr/bin/env python3
"""게시 전 점검 — GitHub Pages에 실제로 올라갈 파일만 골라 용량과 깨진 경로를 본다.

  python3 qa/site_check.py            # 용량 · 경로 점검만
  python3 qa/site_check.py --out DIR  # 게시될 파일을 DIR에 하드링크로 늘어놓는다(브라우저 시험용)

게시 집합 = git 추적 파일 − `_config.yml`의 exclude − 이름이 `_` · `.`으로 시작하는 경로(Jekyll 기본 제외).
GitHub의 실제 빌드를 돌리는 것은 아니다. Jekyll 규칙을 그대로 흉내 낸 것이다.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIMIT_MB = 1000   # GitHub Pages 게시 사이트 한도 1GB
WARN_MB = 900     # 이 선을 넘으면 실패로 친다(여유 100MB)
PAGES = ["index.html", "lessons.html", "saam.html", "tables.html", "pilot_review.html",
         "recall.html", "bagua.html", "narration-review.html"]
ASSET = re.compile(r"""["'(]((?:images|audio|docs)/[^"'()\s<>]+?\.(?:webp|png|jpe?g|svg|mp3|wav|json|csv|txt|md))["')]""")


def read_exclude():
    out, on = [], False
    for line in open(os.path.join(ROOT, "_config.yml"), encoding="utf-8"):
        s = line.split("#", 1)[0].rstrip()
        if not s:
            continue
        if s.startswith("exclude:"):
            on = True
            continue
        if on and s.lstrip().startswith("- "):
            out.append(s.lstrip()[2:].strip().strip("\"'").rstrip("/"))
        elif on:
            on = False
    return out


def published():
    names = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout.split(b"\0")
    ex = read_exclude()
    keep, total = [], 0
    for raw in names:
        if not raw:
            continue
        p = raw.decode("utf-8")
        parts = p.split("/")
        if any(x.startswith("_") or x.startswith(".") for x in parts):
            continue
        if any(p == e or p.startswith(e + "/") for e in ex):
            continue
        full = os.path.join(ROOT, p)
        if not os.path.isfile(full):
            continue
        keep.append(p)
        total += os.path.getsize(full)
    return keep, total, ex


def main():
    keep, total, ex = published()
    have = set(keep)
    mb = total / 1e6
    print(f"exclude: {', '.join(ex)}")
    print(f"게시될 파일 {len(keep)}개 · {mb:.1f}MB (한도 {LIMIT_MB}MB · 경고선 {WARN_MB}MB)")
    bad = 0
    for page in PAGES:
        if page not in have:
            print(f"FAIL 쪽이 게시 집합에 없음: {page}")
            bad += 1
            continue
        text = open(os.path.join(ROOT, page), encoding="utf-8", errors="replace").read()
        refs = sorted(set(m.group(1) for m in ASSET.finditer(text)))
        miss = [r for r in refs if r.split("?")[0] not in have]
        print(f"{'PASS' if not miss else 'FAIL'} {page}: 가리키는 파일 {len(refs)}개 · 없음 {len(miss)}")
        for r in miss[:10]:
            print("     없음:", r)
        bad += len(miss)
    if mb > WARN_MB:
        print(f"FAIL 용량 {mb:.1f}MB > 경고선 {WARN_MB}MB")
        bad += 1
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
        for p in keep:
            dst = os.path.join(out, p)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not os.path.exists(dst):
                try:
                    os.link(os.path.join(ROOT, p), dst)
                except OSError:
                    import shutil
                    shutil.copy2(os.path.join(ROOT, p), dst)
        print(f"게시 집합을 {out} 에 늘어놓음")
    print("결과:", "통과" if bad == 0 else f"문제 {bad}건")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
