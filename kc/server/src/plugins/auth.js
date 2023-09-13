/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                                 //
//                                                                          //
//  WIDE website: http://www.prodvest.com/                                  //
//  WIDE website: http://www.pinyan.tech/                                   //
//  License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)       //
/// //////////////////////////////////////////////////////////////////////////
// Created On : 22 Dec 2022 By 李竺唐 of 北京飞鹿软件技术研究院
// File: auth

'use strict'

const fp = require('fastify-plugin')
// const path = require('path')
module.exports = fp(async function (fastify, opts = {}) {
  const { soa, config } = fastify
  const cfgutil = config.util
  // await soa.get('knex')
  // await util.model(path.join(fastify.dirname, 'src', 'helper', 'models'))
  const passport = await soa.get('passport')
  const strategies = cfgutil.has('passport.strategies') ? cfgutil.get('passport.strategies') : {}
  // // 注册local验证。
  await fastify.reqbase('src/helper/libs/auth/local')(fastify, passport, strategies.local || {})
  // @TODO: 如果是dev模式，注册静态地址。
  // if (cfgutil.isDev()) {
  // }
  // fastify.log.debug('auth opts=', opts)
}, { fastify: '4.x' })
