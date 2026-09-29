import test from "node:test";
import assert from "node:assert/strict";
import {equalInterval, quantile, standardDeviation, jenks} from "./classification.mjs";
test("equal interval",()=>assert.deepEqual(equalInterval([0,10],5),[0,2,4,6,8,10]));
test("quantile keeps bounds",()=>assert.deepEqual(quantile([1,2,3,4,5],2),[1,3,5]));
test("missing values",()=>assert.deepEqual(standardDeviation([NaN]),[]));
test("jenks keeps range and class count",()=>{const b=jenks([1,2,2,3,50,51,52],2);assert.equal(b.length,3);assert.equal(b[0],1);assert.equal(b.at(-1),52)});
