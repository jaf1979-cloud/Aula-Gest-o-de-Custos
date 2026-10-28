const fs=require('fs');
const {Document,Packer,Paragraph,TextRun,Table,TableRow,TableCell,WidthType,ShadingType,AlignmentType,BorderStyle,LevelFormat,PageBreak,Header,Footer,PageNumber,HeadingLevel}=require('docx');
const EX=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const fmt=(v,nd=2)=>v.toLocaleString('pt-BR',{minimumFractionDigits:nd,maximumFractionDigits:nd});
const qn=v=>v.toLocaleString('pt-BR');
const F='Arial', NAVY='0B2A63';
const brd={style:BorderStyle.SINGLE,size:4,color:'9AA8B8'};
const borders={top:brd,bottom:brd,left:brd,right:brd};
const P=(runs,opt={})=>new Paragraph({spacing:{after:80,line:264},...opt,children:(Array.isArray(runs)?runs:[runs]).map(r=>typeof r==='string'?new TextRun({text:r,font:F,size:22}):r)});
const T=(t,o={})=>new TextRun({text:t,font:F,size:22,...o});
function cell(text,w,{head=false,right=false,bold=false}={}){
  return new TableCell({borders,width:{size:w,type:WidthType.DXA},margins:{top:30,bottom:30,left:100,right:100},
    shading:head?{fill:'EAF1F5',type:ShadingType.CLEAR,color:'auto'}:undefined,
    children:[new Paragraph({spacing:{after:0,line:240},alignment:right?AlignmentType.RIGHT:AlignmentType.LEFT,children:[new TextRun({text,font:F,size:head?17:19,bold:head||bold,color:head?NAVY:undefined})]})]});
}
function table(widths,head,rows,rightCols){
  const total=widths.reduce((a,b)=>a+b,0);
  return new Table({width:{size:total,type:WidthType.DXA},columnWidths:widths,rows:[
    new TableRow({tableHeader:true,children:head.map((h,i)=>cell(h,widths[i],{head:true,right:rightCols.includes(i)}))}),
    ...rows.map(r=>new TableRow({children:r.map((c,i)=>cell(c,widths[i],{right:rightCols.includes(i)}))}))]});
}
const children=[];
children.push(new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:60},children:[T('UTFPR · GESTÃO DE CUSTOS',{bold:true,size:20,color:'5A6878'})]}));
children.push(new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:120},children:[T('Custeio por Absorção Integral, Absorção Ideal e pela Margem de Contribuição',{bold:true,size:26,color:NAVY})]}));
children.push(new Paragraph({spacing:{after:240},border:{bottom:{style:BorderStyle.SINGLE,size:8,color:'0F9E93',space:4}},children:[T('Nome: ____________________________________   RA: ___________   Data: ___/___/_____',{size:20})]}));
children.push(P([T('Instruções para as respostas: ',{bold:true}),T('não utilizar ponto para milhar e usar vírgula para as decimais nos valores monetários (ex.: 100200,00). Utilizar 2 casas após a vírgula para valores monetários (ex.: 200,00) e para valores em percentual, sem o símbolo % (ex.: 13,56).')]));
EX.forEach((e,k)=>{
  if(k>0) children.push(new Paragraph({children:[new PageBreak()]}));
  children.push(new Paragraph({heading:HeadingLevel.HEADING_1,spacing:{before:120,after:120},children:[T(`Exercício ${e.n} · ${e.ind}`,{bold:true,size:28,color:NAVY})]}));
  children.push(P([T('A '),T(e.empresa.toUpperCase(),{bold:true}),T(`, de ${e.cidade}, faturou `),T(`R$ ${fmt(e.R)}`,{bold:true}),T(' no mês corrente e teve os seguintes custos:')]));
  {const h=Math.ceil(e.gastos.length/2), rows=[];
  for(let i=0;i<h;i++){const a=e.gastos[i], b=e.gastos[i+h]; rows.push([a[0],fmt(a[1]),b?b[0]:'',b?fmt(b[1]):'']);}
  children.push(table([2950,1550,2950,1550],['Gasto','R$','Gasto','R$'],rows,[1,3]));}
  children.push(P([T('Sabe-se que:',{bold:true})],{spacing:{before:240,after:120}}));
  children.push(table([2900,1300,1250,1250,1300,1300],['Produto','Matéria-prima (R$/un.)','Quantidade vendida','Produção do mês','Preço praticado (R$)','Margem de lucro'],
    e.prods.map(p=>[p.desc,fmt(p.mp),qn(p.qv),qn(p.qp),fmt(p.pv),`${p.L}%`]),[1,2,3,4,5]));
  children.push(P('Calcular os custos dos produtos e os preços de venda pelos métodos de CUSTEIO POR ABSORÇÃO INTEGRAL, CUSTEIO POR ABSORÇÃO IDEAL e CUSTEIO PELA MARGEM DE CONTRIBUIÇÃO, garantindo as margens de lucro indicadas na tabela.',{spacing:{before:200,after:60}}));
  children.push(P('Pede-se:',{spacing:{before:200,after:60}}));
  ['Elaborar o DRE sintético (receita, CVV, CVP, custo fixo e lucro operacional).',
   'Calcular o CF unitário, o custo total e o preço de venda pela absorção integral.',
   'Calcular o CF unitário, o custo total e o preço de venda pela absorção ideal.',
   'Calcular a MC total %, o CF unitário, o custo total e o preço de venda pela margem de contribuição.',
   'Comparar os três métodos com o preço praticado e interpretar as diferenças.'].forEach(t=>
     children.push(new Paragraph({numbering:{reference:`ped${e.n}`,level:0},spacing:{after:60},children:[T(t)]})));
});
const doc=new Document({styles:{default:{document:{run:{font:F,size:22}}}},
  numbering:{config:EX.map(e=>({reference:`ped${e.n}`,levels:[{level:0,format:LevelFormat.LOWER_LETTER,text:'%1)',alignment:AlignmentType.LEFT,style:{paragraph:{indent:{left:567,hanging:340}}}}]}))},
  sections:[{properties:{page:{size:{width:11906,height:16838},margin:{top:850,bottom:850,left:1304,right:1304}}},
    footers:{default:new Footer({children:[new Paragraph({alignment:AlignmentType.CENTER,children:[T('Prof. José Ângelo Ferreira · Gestão de Custos · UTFPR · página ',{size:16,color:'5A6878'}),new TextRun({children:[PageNumber.CURRENT],font:F,size:16,color:'5A6878'})]})]})},
    children}]});
Packer.toBuffer(doc).then(b=>fs.writeFileSync(process.argv[3],b));
