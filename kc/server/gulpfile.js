/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                               //
//                                                                         //
//  WIDE website: http://www.wware.org/                                    //
//  WIDE website: http://www.prodvest.com/                                 //
//  License : WWARE LICENSE(https://www.wware.org/license.html)            //
/// /////////////////////////////////////////////////////////////////////////
// Created On : 6 Oct 2022 By 李竺唐 of SanPolo.Co.LTD
// File: index

const gulpInst = require('gulp')
const soa = require('@masol/soa')
const AWS = require('aws-sdk')
const os = require('os')

// 添加默认并发限制为核心数X2，目前只影响通过SFTP上下传目录时的并发，尚未影响node操作
const args = require('yargs')
  .alias('t', 'target')
  .alias('s', 'stage')
  .alias('m', 'mirror')
  .alias('c', 'concurrency')
  .boolean('force')
  .boolean('mirror')
  .boolean('dry-run') // 不真正执行部署bash，而是将内容拷贝到服务器后结束。用于调试生成的脚本。
  .default('concurrency', Math.ceil(os.cpus().length / 2))
  .default('target', 'dev')
  .default('dry-run', false)
  .default('stage', 'check')
  .default('mirror', false)
  .default('force', false)
  .argv

const path = require('path')
process.env.NODE_CONFIG_DIR = process.env.NODE_CONFIG_DIR || path.join(__dirname, 'config', args.target)
const config = require('config')

const opts = {
  args,
  config,
  gulpInst,
  AWS,
  ctx: {},
  soa: soa.getUtil(config)
}

module.exports = require('@masol/pipeline')(opts)
