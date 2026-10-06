const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const output = path.join(root, 'docs');
fs.mkdirSync(output, { recursive: true });
for (const name of ['index.html', 'style.css', 'data.js', 'storage.js', 'cloud.js', 'app.js']) {
  fs.copyFileSync(path.join(root, 'dist', name), path.join(output, name));
}
const config=fs.readFileSync(path.join(root,'dist/config.js'),'utf8').replace('hosted: false','hosted: true');
fs.writeFileSync(path.join(output, 'config.js'), config);
fs.writeFileSync(path.join(output, '.nojekyll'), '');
fs.mkdirSync(path.join(output, 'books'), { recursive: true });
for (const [key, name] of Object.entries({ full: '青山学堂GRE全能词.pdf', precise: '青山学堂GRE词表-精准释义V1.0.pdf', rare: '青山学堂GRE词表-熟词僻义V1.0.pdf', pairs: '青山学堂GRE词表-等价词对V2.0.pdf', zhen: '真经GRE等价词汇总.pdf' })) {
  fs.copyFileSync(path.join(root, '资料原件', name), path.join(output, 'books', key + '.pdf'));
}
const html = fs.readFileSync(path.join(output, 'index.html'), 'utf8');
for (const [, ref] of html.matchAll(/(?:src|href)="([^"#]+)"/g)) {
  if (!ref.startsWith('data:') && !fs.existsSync(path.join(output, ref))) throw Error('Missing public asset: ' + ref);
}
console.log('GitHub Pages output ready: docs/');
