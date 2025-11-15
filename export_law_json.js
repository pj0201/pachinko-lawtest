// lawDatabase.jsをJSONとして出力するスクリプト
const { WIND_BUSINESS_LAW } = require('./src/constants/lawDatabase.js');
console.log(JSON.stringify(WIND_BUSINESS_LAW, null, 2));
