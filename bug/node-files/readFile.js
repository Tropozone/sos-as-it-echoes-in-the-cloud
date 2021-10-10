const fs = require('fs').promises; //use the fs module to interact with the filesystem. Notice, though, that you are importing the .promises part of the module.


// asynchronous code
async function readFile(filePath) {
try {
    const data = await fs.readFile(filePath);
    console.log(data.toString());
} catch (error) {
    console.error(`Got an error trying to read the file: ${error.message}`);
}
}

readFile('greetings.txt');

