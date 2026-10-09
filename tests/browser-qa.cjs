/* Run against tests/serve.py; dependencies and screenshots stay in a QA folder. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require(process.env.QA_PLAYWRIGHT_MODULE || 'playwright');
const output = process.env.QA_OUTPUT_ROOT;
if (!output) throw Error('Set QA_OUTPUT_ROOT to the approved evidence directory.');
fs.mkdirSync(output, {recursive:true});
const base = 'http://127.0.0.1:4174';
const locales = ['ko','en','ja','de','fr','es','pt-BR'];
const messages = Object.fromEntries(locales.map(code => [code, JSON.parse(fs.readFileSync(path.join(__dirname,'../data/locales',code+'.json')))]));
const records = [], errors = [];
let browser;
const format = (copy, values) => copy.replace(/\{(\w+)\}/g, (_,key) => values[key]);
async function test(name, fn) {
  try {await fn();records.push({name,status:'PASS'}); if (name.startsWith('language switching')) console.log('PASS',name);}
  catch(e) {records.push({name,status:'FAIL',error:String(e)});throw e;}
}
async function context(options={}) {
  const ctx = await browser.newContext(options);
  ctx.on('page', page => page.on('pageerror', e => errors.push(String(e))));
  return ctx;
}
(async () => {
  browser = await chromium.launch({headless:true, executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args:['--disable-background-networking']});
  const ctx = await context({locale:'en-US'});
  const page = await ctx.newPage();
  for (const code of locales) {
    for (const route of ['/', '/apps/', '/games/', '/404.html']) {
      for (const width of [320,390,768,1024,1440]) {
        await test(`layout ${code}${route} width=${width}`, async () => {
          await page.setViewportSize({width,height:900});
          await page.goto(base+'/'+code+route);
          await page.evaluate(() => document.fonts.ready);
          assert.equal(await page.getAttribute('html','lang'),code);
          const metrics = await page.evaluate(() => {
            const outside=[];
            for (const el of document.querySelectorAll('h1,h2,h3,.site-header,.site-nav,.header-tools,.project-card,.button,.contact-inner a')) {
              const r=el.getBoundingClientRect();
              if (r.width && (r.left < -1 || r.right > innerWidth+1)) outside.push({tag:el.tagName,class:el.className,left:r.left,right:r.right});
            }
            return {overflow:document.documentElement.scrollWidth>innerWidth+1,outside};
          });
          assert.deepEqual(metrics,{overflow:false,outside:[]});
          assert.equal(await page.locator('.language-picker summary').count(),1);
          await page.locator('.language-picker summary').click();
          assert.equal(await page.locator('[data-language]:visible').count(),7);
          assert.equal(await page.locator(`[data-language="${code}"]`).getAttribute('aria-current'),'true');
          await page.keyboard.press('Escape');
          assert.equal(await page.locator('.language-picker').getAttribute('open'),null);
          if (route==='/' || route==='/games/') {
            if ([320,1440].includes(width)) await page.screenshot({path:path.join(output,`${code}-${route==='/'?'home':'games'}-${width}.png`),fullPage:true});
          }
        });
      }
    }
    await test(`search/filter/reset ${code}`, async () => {
      await page.goto(base+'/'+code+'/games/');
      const input=page.locator('input[type=search]');
      await input.fill('Facet');
      assert.equal(await page.locator('[data-project]:visible').count(),1);
      assert.equal(await page.locator('[data-result-count]').textContent(),format(messages[code]['count.filtered'],{count:1,total:3}));
      await input.fill('zzzz unmatched');
      assert.equal(await page.locator('.empty-state:visible').count(),1);
      assert.equal(await page.locator('[data-release-group]:visible').count(),0);
      await page.locator('[data-reset]').click();
      assert.equal(await page.locator('[data-project]:visible').count(),3);
      assert.equal(await page.evaluate(() => document.activeElement.type),'search');
      await page.locator('[data-filter="스토리"]').click();
      assert.equal(await page.locator('[data-project]:visible').count(),1);
      assert.equal(await page.locator('[data-project]:visible h3').textContent(),'달빛 고물상Moonjunk Workshop');
      await page.locator('[data-filter=""]').click();
      await input.fill(messages[code]['tag.리듬']);
      assert.equal(await page.locator('[data-project]:visible').count(),1);
    });
    await test(`language switching and refresh ${code}`, async () => {
      await page.goto(base+'/en/games/?ref=review#project-list');
      await page.locator('.language-picker summary').click();
      await page.locator(`[data-language="${code}"]`).click();
      assert.equal(new URL(page.url()).pathname,'/'+code+'/games/');
      assert.equal(new URL(page.url()).search,'?ref=review');
      assert.equal(new URL(page.url()).hash,'#project-list');
      await page.reload();
      assert.equal(await page.getAttribute('html','lang'),code);
      await page.goto(base+'/apps/');
      assert.equal(new URL(page.url()).pathname,'/'+code+'/apps/');
    });
  }
  await test('keyboard skip link and language menu', async () => {
    await page.goto(base+'/en/');
    await page.keyboard.press('Tab');
    assert.equal(await page.evaluate(() => document.activeElement.className),'skip-link');
    await page.keyboard.press('Enter');
    assert.equal(new URL(page.url()).hash,'#main');
    assert.equal(await page.evaluate(() => document.activeElement.id),'main');
    await page.locator('.language-picker summary').focus();
    await page.keyboard.press('Enter');
    assert.equal(await page.locator('[data-language]:visible').count(),7);
    await page.keyboard.press('Tab');
    assert.equal(await page.evaluate(() => document.activeElement.dataset.language),'ko');
    await page.keyboard.press('Enter');
    assert.equal(await page.getAttribute('html','lang'),'ko');
  });
  for (const [locale,expected] of [['fr-FR','fr'],['ja-JP','ja'],['pt-PT','pt-BR'],['zh-CN','en']]) {
    await test(`browser language fallback ${locale}`, async () => {
      const c=await context({locale});const p=await c.newPage();
      await p.goto(base+'/games/');
      await p.waitForURL('**/'+expected+'/games/');
      assert.equal(await p.getAttribute('html','lang'),expected);
      await c.close();
    });
  }
  await test('browser language list skips unsupported preferences', async () => {
    const c=await context();
    await c.addInitScript(() => Object.defineProperty(navigator,'languages',{value:['zh-CN','es-MX','fr-FR']}));
    const p=await c.newPage();await p.goto(base+'/');await p.waitForURL('**/es/');
    assert.equal(await p.getAttribute('html','lang'),'es');await c.close();
  });
  await test('URL language overrides browser and stored preference', async () => {
    const c=await context({locale:'ja-JP'});const p=await c.newPage();
    await p.goto(base+'/fr/');
    await p.goto(base+'/apps/?lang=ko&ref=link#project-list');
    await p.waitForURL('**/ko/apps/?ref=link#project-list');
    assert.equal(await p.getAttribute('html','lang'),'ko');
    await p.goto(base+'/de/games/');
    assert.equal(await p.getAttribute('html','lang'),'de');
    await c.close();
  });
  await test('storage disabled remains usable', async () => {
    const c=await context({locale:'ja-JP'});
    await c.addInitScript(() => {Storage.prototype.getItem=Storage.prototype.setItem=()=>{throw new DOMException('blocked','SecurityError')};});
    const p=await c.newPage();await p.goto(base+'/apps/');await p.waitForURL('**/ja/apps/');
    await p.goto(base+'/de/games/');assert.equal(await p.getAttribute('html','lang'),'de');
    await p.locator('.language-picker summary').click();await p.locator('[data-language="fr"]').click();
    assert.equal(await p.getAttribute('html','lang'),'fr');await c.close();
  });
  await test('localized custom 404', async () => {
    await page.goto(base+'/ja/missing-path/');
    await page.waitForURL('**/ja/404.html');
    assert.equal(await page.getAttribute('html','lang'),'ja');
    assert.equal(await page.locator('meta[name=robots]').getAttribute('content'),'noindex');
  });
  await test('content and language links without JavaScript', async () => {
    const c=await context({javaScriptEnabled:false});const p=await c.newPage();
    for (const code of locales) {
      await p.goto(base+'/'+code+'/games/');
      assert.equal(await p.locator('[data-project]').count(),3);
      await p.locator('.language-picker summary').click();
      assert.equal(await p.locator('[data-language]:visible').count(),7);
    }
    await p.locator('[data-language="ja"]').click();assert.equal(new URL(p.url()).pathname,'/ja/games/');
    await c.close();
  });
  assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(output,'result.json'),JSON.stringify({status:'PASS',browser:await browser.version(),checks:records.length,records,pageErrors:errors},null,2));
  console.log(`PASS ${records.length} browser checks; screenshots: ${output}`);
})().catch(error => {
  fs.writeFileSync(path.join(output,'result.json'),JSON.stringify({status:'FAIL',records,pageErrors:errors,error:String(error)},null,2));
  console.error(error);process.exitCode=1;
}).finally(async () => {if(browser) await browser.close();});
