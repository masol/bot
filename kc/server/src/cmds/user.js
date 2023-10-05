/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                               //
//                                                                         //
//  WIDE website: http://www.wware.org/                                    //
//  WIDE website: http://www.prodvest.com/                                 //
//  License : WWARE LICENSE(https://www.wware.org/license.html)            //
/// /////////////////////////////////////////////////////////////////////////
// Created On : 22 Sep 2022 By 李竺唐 of SanPolo.Co.LTD
// File: init

const fs = require('fs').promises
const crypto = require('crypto')

module.exports.dep = 'migrate'

module.exports.run = async function (fastify, opts = {}) {
  const { soa, _, log, config, runcmd } = fastify
  const cfgutil = config.util
  const ojs = await soa.get('objection')
  const Users = ojs.Model.store.users
  if (!Users) {
    log.error('未注册用户表!')
    return false
  }

  // console.log('Users=', Users)
  const admin = await Users.query()
    .select('id')
    .where('accountName', 'admin')
  // console.log('admin=', admin)

  if (admin.length === 1 && !runcmd.reset) {
    log.warn('用户admin已经存在，请添加reset参数来重置密码')
    return false
  }
  const pwdFile = cfgutil.path('config', 'active', 'admin.passwd')

  let passwd = await fs.readFile(pwdFile, 'utf8').catch(e => {
    return ''
  })

  if (!passwd) {
    passwd = _.cryptoRandom({ length: 16 })
    await fs.writeFile(pwdFile, passwd)
  }

  let result
  if (admin.length > 0) {
    result = await Users.query().update({
      password: crypto.createHash('md5').update(passwd).digest('hex'),
      active: true
    }).where('accountName', 'admin')
  } else {
    result = await Users.query().insert({
      accountName: 'admin',
      password: crypto.createHash('md5').update(passwd).digest('hex'),
      active: true,
      role: [0]
    })
  }
  log.info(`用户admin创建完毕，密码文件:${pwdFile}`)
  // console.log('result=', result)
  return result
}
