const { chromium } = require('playwright');
const D = process.argv[2] || __dirname + '/';   // 캡처 저장 위치
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
  await p.goto('file://' + (process.env.SF || '/home/user/Shorts-Factory') + '/web/index.html');   // 서버 없이 파일로 열기(샘플 모드)
  await p.waitForTimeout(2000);
  await p.evaluate(() => { LIVE = false; });
  await p.fill('#linkInput', 'https://youtu.be/풀영상-링크');
  await p.click('#countPick [data-n="3"]');
  await p.screenshot({ path: D + 'd_home.png' });
  await (await p.$('#countPick')).screenshot({ path: D + 'd_count.png' });
  await p.evaluate(() => openConsent());
  await p.waitForTimeout(400);
  await (await p.$('#consent .modal-box')).screenshot({ path: D + 'd_consent.png' });
  await p.evaluate(() => document.querySelector('#consent').classList.remove('open'));
  await p.evaluate(() => runSample());
  await p.waitForTimeout(4200);
  await p.screenshot({ path: D + 'd_working.png' });
  await p.waitForTimeout(5000);
  await p.evaluate(() => {
    state = fromSample().slice(0, 3);
    state.forEach((s, i) => { s.opts = defOpts(['bigblack', 'simple', 'full'][i]); });
    renderCards(); go('results');
  });
  await p.waitForTimeout(2500);
  await p.screenshot({ path: D + 'd_results.png' });
  await p.evaluate(() => openEditor(0));
  await p.waitForTimeout(2000);
  await p.screenshot({ path: D + 'd_editor.png' });
  await (await p.$('.phone')).screenshot({ path: D + 'd_phone.png' });
  await p.check('#voiceOn');
  await p.click('#voiceF [data-v="Aoede"]');
  await (await p.$('#voiceBox')).screenshot({ path: D + 'd_voice.png' });
  await b.close();
})();
