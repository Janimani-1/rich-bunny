import sys, time
from playwright.sync_api import sync_playwright

page_path, out = sys.argv[1], sys.argv[2]
errors = []
with sync_playwright() as p:
    br = p.chromium.launch(executable_path="/usr/bin/google-chrome", headless=True,
                           args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    pg = br.new_page(viewport={"width": 412, "height": 860}, device_scale_factor=1, has_touch=True)
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" and "ERR_TUNNEL" not in m.text else None)
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto("file://" + page_path)
    time.sleep(1)
    pg.evaluate("__g.stop()")
    sim = lambda s: pg.evaluate(f"__g.sim({s})")
    shot = lambda n: pg.screenshot(path=f"{out}/{n}.png")
    sim(0.5); shot("01_ready")
    # تست لمس واقعی: ضربه برای شروع
    pg.touchscreen.tap(200, 500); sim(1.5); shot("02_run")
    print("after tap state:", pg.evaluate("__g.state"))
    pg.evaluate("__g.swipe('L')"); sim(0.25); shot("03_left")
    pg.evaluate("__g.swipe('U')"); sim(0.3); shot("04_jump")
    sim(0.6)
    pg.evaluate("__g.swipe('D')"); sim(0.2); shot("05_slide")
    sim(0.6)
    pg.evaluate("__g.hurt()")
    for i, t in enumerate([0.4, 0.5, 0.5, 0.5, 0.5]):
        sim(t); shot(f"06_dizzy_{i}")
    sim(1.0); print("after dizzy:", pg.evaluate("__g.state"))
    pg.evaluate("__g.jumpTo(-512)"); sim(1.5); shot("07_finish_a")
    sim(2.5); shot("08_finish_b")
    print("final:", pg.evaluate("__g.state"), "carrots", pg.evaluate("__g.B.carrots"))
    br.close()
print("ERRORS:", errors)
