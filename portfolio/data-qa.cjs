const fs=require('node:fs');
const own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
const blank=v=>typeof v==='string' && v.trim()==='';
function audit(input){
  if(!input || typeof input!=='object' || Array.isArray(input) || Buffer.byteLength(JSON.stringify(input))>75000)throw new Error('Input must be a JSON object of at most 75000 bytes');
  if(Object.keys(input).some(k=>!['rows','requiredFields','uniqueFields'].includes(k)))throw new Error('Unexpected input field');
  const {rows,requiredFields,uniqueFields}=input;
  if(!Array.isArray(rows)||rows.length>100||rows.some(r=>!r||typeof r!=='object'||Array.isArray(r)||Object.keys(r).length>20||Object.entries(r).some(([k,v])=>!k||k.length>100||!['string','number','boolean'].includes(typeof v)&&v!==null||typeof v==='string'&&v.length>2000||typeof v==='number'&&!Number.isFinite(v))))throw new Error('Rows must contain at most 100 flat objects, 20 fields each, with scalar or null values');
  for(const fields of [requiredFields,uniqueFields])if(!Array.isArray(fields)||fields.length>20||new Set(fields).size!==fields.length||fields.some(f=>typeof f!=='string'||!f||f.length>100))throw new Error('Field rules must be distinct string arrays of at most 20 names');
  const issues=[];
  rows.forEach((r,i)=>{for(const field of requiredFields){const code=!own(r,field)?'MISSING':r[field]===null?'NULL':blank(r[field])?'BLANK':null;if(code)issues.push({row:i+1,field,code,firstRow:null});}});
  for(const field of uniqueFields){const seen=new Map();rows.forEach((r,i)=>{if(!own(r,field)||r[field]===null||blank(r[field]))return;const key=typeof r[field]+':'+JSON.stringify(r[field]);if(seen.has(key))issues.push({row:i+1,field,code:'DUPLICATE',firstRow:seen.get(key)});else seen.set(key,i+1);});}
  const cmp=(a,b)=>a<b?-1:a>b?1:0;
  issues.sort((a,b)=>a.row-b.row||cmp(a.field,b.field)||cmp(a.code,b.code));
  return {rowCount:rows.length,fieldNames:[...new Set(rows.flatMap(Object.keys))].sort(cmp),valid:issues.length===0,issueCount:issues.length,rowsWithIssues:new Set(issues.map(x=>x.row)).size,issues};
}
module.exports={audit};
if(require.main===module){const input=JSON.parse(fs.readFileSync(process.argv[2],'utf8').replace(/^\uFEFF/,''));process.stdout.write(JSON.stringify(audit(input),null,2)+'\n');}
