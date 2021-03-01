const fs = require('fs');


let rawdata = fs.readFileSync('./data/query.json');
let queries = JSON.parse(rawdata); //need a list. for now only one element look at >>
console.dir(queries, {depth: null, colors: true});

const se_scraper = require('./se-scraper');
const nPage=1;
var links="";
var newlink="";

//Load the terms in the text file
//var text = fs.readFileSync("./data/query2.txt").toString('utf-8');
//var queries = text.split("\n");
//console.dir(queries, {depth: null, colors: true});

(async () => {

    let scrape_job = {
        search_engine: 'google', //duckduckgo'
        keywords: queries, //list queries. Could have only one
        num_pages: nPage,
    };

//SCRAPER
    var results = await se_scraper.scrape({}, scrape_job);
    var linksDict = new Object();//DOES not work for now ??>>>
//EXTRACT ONLY LINKS
    var i;   var q;   var j;
      for (q = 0; q < queries.length; q++) {
        linksDict[queries[q]]=[]
      for (i = 1; i <= nPage; i++) {
      res=results['results'][queries[q]][i].results
      for (j = 0; j < res.length; j++) {
      newlink=res[j]['link'];//'visible_link' >>sometimes need other for dzckduck ?
      newlink=newlink.concat(' \n');
      linksDict[queries[q]].push(newlink) //dictionary of ...
      console.dir(linksDict[queries[q]], {depth: null, colors: true})
      links=links.concat(newlink);
      console.dir(newlink, {depth: null, colors: true});
      }
    }
    // SAVE FILE
    if (q==queries.length-1) {
    var dictstring = JSON.stringify(linksDict);
    console.dir(dictstring, {depth: null, colors: true})
    fs.writeFile('./data/links.json', dictstring, (err) => {
        if (err) throw err;   // In case of a error throw err.
    })
    fs.writeFile('./data/links.txt', links, (err) => {
        if (err) throw err;   // In case of a error throw err.
    })
  }
}
})();

