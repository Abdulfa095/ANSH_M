const fs = require('fs');
const path = require('path');

function replaceInFile(filePath) {
    let content = fs.readFileSync(filePath, 'utf8');
    
    // Replace standard single quote URLs: 'http://localhost:8000/api/...' -> `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/...`
    content = content.replace(/'http:\/\/localhost:8000([^']*)'/g, '`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}$1`');
    
    // Replace backtick URLs: `http://localhost:8000/api/...` -> `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/...`
    content = content.replace(/`http:\/\/localhost:8000([^`]*)`/g, '`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}$1`');
    
    // Replace double quote URLs inside URL objects or similar: new URL("http://localhost:8000/api/...")
    content = content.replace(/"http:\/\/localhost:8000([^"]*)"/g, '`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}$1`');

    fs.writeFileSync(filePath, content);
}

const files = [
    'app/[locale]/register/page.tsx',
    'app/[locale]/login/page.tsx',
    'app/[locale]/subscribe/page.tsx',
    'app/[locale]/admin/page.tsx',
    'components/MandiFinder.tsx',
    'app/[locale]/page.tsx'
];

files.forEach(f => {
    const p = path.join(__dirname, f);
    if(fs.existsSync(p)) {
        replaceInFile(p);
    }
});
console.log('Replaced localhost:8000 with process.env.NEXT_PUBLIC_API_URL');
