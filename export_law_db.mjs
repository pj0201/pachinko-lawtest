#!/usr/bin/env node
// lawDatabase.jsからJSON export
import { WIND_BUSINESS_LAW } from './src/constants/lawDatabase.js';
import fs from 'fs';

// JSONファイルに出力
fs.writeFileSync('law_database.json', JSON.stringify(WIND_BUSINESS_LAW, null, 2), 'utf-8');
console.log('lawDatabase.jsをJSONに変換しました: law_database.json');
