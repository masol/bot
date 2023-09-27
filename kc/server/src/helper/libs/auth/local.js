/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                                 //
//                                                                          //
//  WIDE website: http://www.prodvest.com/                                  //
//  WIDE website: http://www.pinyan.tech/                                   //
//  License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)       //
/// //////////////////////////////////////////////////////////////////////////
// Created On : 22 Dec 2022 By 李竺唐 of 北京飞鹿软件技术研究院
// File: local

const crypto = require('crypto')

module.exports = async function (fastify, passport, conf) {
  // console.log('passport.module.Strategy=', passport.module.Strategy)
  const { shell, _, config, soa } = fastify
  const cfgutil = config.util
  const defName = cfgutil.dget('passport.strategies.local.defaultName', '未命名')
  // 允许用户名密码登录的用户名正则。默认为'.*',全部允许。设置为false禁止用户名密码登录。
  const pwdRE = cfgutil.dget('passport.strategies.local.pwdRE', '.*')
  const LocalStrategy = await shell.import('passport-local')
  // console.log('LocalStrategy=', LocalStrategy)
  passport.use('local', new LocalStrategy.Strategy(async function (username, password, done) {
    const ojs = await soa.get('objection')
    const Users = ojs.Model.store.users
    const colName = await Users.colName(fastify, username)

    let row = false
    // if (colName && pwdRE) {
    if (colName) {
      // if (pwdRE === '.*' || new RegExp(pwdRE).text(username)) {
      if (!pwdRE || (new RegExp(pwdRE)).test(password)) {
        const ojs = await soa.get('objection')
        const Users = ojs.Model.store.users
        const user = await Users.query()
          .select('*') // 'id', 'accountName', 'nickName', 'commonName', 'email', 'mobile', 'name', 'idcard', 'password', 'avatar', 'role', 'group', 'active', 'ota', 'otaExpire')
          .where(colName, username)
          .limit(2)
        if (user.length === 1) {
          const u = user[0]
          if (u.active) {
            if (u.password === crypto.createHash('md5').update(password).digest('hex')) {
              row = _.pick(u, ['id', 'avatar', 'role', 'group'])
              row.name = u.nickName || u.commonName || u.email || u.mobile || u.name || u.accountName || u.idcard || defName
            }
          }
        }
      }
    }
    // console.log('local login=', username, passport)
    // const row = { username: 'test', role: ['a', 'b', 'c'] }
    done(null, row)
    // console.log('after cb!!row=', row)
  }))
  //
}
