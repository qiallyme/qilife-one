const path = require('path');
const fs = require('fs');

describe('QiLife App', () => {
  test('main entry point exists', () => {
    const mainPath = path.join(__dirname, '..', 'app', 'main', 'main.js');
    expect(fs.existsSync(mainPath)).toBe(true);
  });

  test('preload script exists', () => {
    const preloadPath = path.join(__dirname, '..', 'app', 'main', 'preload.js');
    expect(fs.existsSync(preloadPath)).toBe(true);
  });

  test('index.html exists', () => {
    const indexPath = path.join(__dirname, '..', 'index.html');
    expect(fs.existsSync(indexPath)).toBe(true);
  });

  test('package.json has required scripts', () => {
    const packagePath = path.join(__dirname, '..', 'package.json');
    const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
    
    expect(packageJson.scripts.dev).toBeDefined();
    expect(packageJson.scripts.build).toBeDefined();
    expect(packageJson.scripts.start).toBeDefined();
  });
}); 