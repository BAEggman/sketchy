// FULLDECK 배열을 괄호 매칭으로 잘라 JSON으로 저장
const fs=require('fs');
const src=fs.readFileSync(process.argv[2],'utf8');
const i=src.indexOf('const FULLDECK = [');
if(i<0){console.error('no FULLDECK');process.exit(1)}
let j=src.indexOf('[',i), d=0, k=j, inS=null, esc=false;
for(;k<src.length;k++){const c=src[k];
 if(inS){ if(esc){esc=false;continue} if(c==='\\'){esc=true;continue} if(c===inS){inS=null} continue }
 if(c==='"'||c==="'"||c==='`'){inS=c;continue}
 if(c==='[')d++; else if(c===']'){d--; if(d===0)break}}
const arr=new Function('return '+src.slice(j,k+1))();
fs.writeFileSync(process.argv[3],JSON.stringify(arr,null,0));
console.log(arr.length, Object.keys(arr[0]));
console.log(JSON.stringify(arr[0]).slice(0,800));
