/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                               //
//                                                                         //
//  WIDE website: http://www.wware.org/                                    //
//  WIDE website: http://www.prodvest.com/                                 //
//  License : WWARE LICENSE(https://www.wware.org/license.html)            //
/// /////////////////////////////////////////////////////////////////////////
// Created On : 20 Sep 2022 By 李竺唐 of SanPolo.Co.LTD
// File: v1

const USER = 'users'
const AUDIT = 'audit'
// const INVITE = 'invite'
// const OAUTH = 'oauth'
module.exports = function (fastify, opts) {
  return {
    async up (knex) {
      // await knex.raw('CREATE SCHEMA IF NOT EXISTS ??', AUTH)
      // return knex.schema.withSchema(AUTH)
      await knex.schema
        .createTable(USER, function (table) {
          table.uuid('id', { primaryKey: true }).defaultTo(knex.raw('gen_random_uuid()'))
          // 帐号名，可空。
          table.string('accountName', 128).unique().nullable()
          // 密码md5。
          table.string('password', 128).nullable()
          // ota密码。
          table.string('ota', 128).nullable()
          // ota失效时间。
          table.string('otaExpire', 128).nullable()
          // 昵称
          table.string('nickName', 128).nullable()
          // 显示用真实名
          table.string('commonName', 32).nullable()
          // 邮箱地址
          table.string('email', 128).unique().nullable()
          // 邮箱地址已验证。
          table.boolean('emailVerified').defaultTo(false)
          // 手机号码
          table.string('mobile', 32).unique().nullable()
          // 手机号码已验证。
          table.boolean('mobileVerified').defaultTo(false)
          // 电话号码
          table.string('phone', 32).unique().nullable()
          // 电话号码已验证。
          table.boolean('phoneVerified').defaultTo(false)
          // 真实姓名
          table.string('name', 32).nullable()
          // 真实姓名已验证(身份证验证)
          table.boolean('nameVerified').defaultTo(false)
          // 身份证号
          table.string('idcard', 64).unique().nullable()
          // 身份证号已验证(身份证验证)
          table.boolean('idcardVerified').defaultTo(false)
          // oauth uuid slot 1
          table.string('exa1', 64).unique().nullable()
          // oauth uuid slot 2
          table.string('exa2', 64).unique().nullable()
          // oauth uuid slot 3
          table.string('exa3', 64).unique().nullable()
          // oauth uuid slot 4
          table.string('exa4', 64).unique().nullable()
          // oauth uuid slot 5
          table.string('exa5', 64).unique().nullable()
          // oauth uuid slot 6
          table.string('exa6', 64).unique().nullable()
          // oauth uuid slot 7
          table.string('exa7', 64).unique().nullable()
          // oauth uuid slot 8
          table.string('exa8', 64).unique().nullable()
          // oauth uuid slot 9
          table.string('exa9', 64).unique().nullable()
          // 是否激活,多重验证中间状态，或者管理员临时禁用用户。
          table.boolean('active').defaultTo(false)
          // 创建日期。
          table.timestamp('createdAt').notNullable().defaultTo(knex.fn.now())
          // 创建人
          table.uuid('createdBy').nullable()
          // avatar(URL)
          table.text('avatar').nullable()
          // 用户备注
          table.text('note').nullable()
          // 逗号分割的下一动作序列(激发状态变化)。
          table.string('nextAction', 255).nullable()
          // 所属角色,采用数字数组。
          table.specificType('role', 'integer ARRAY').nullable()
          // 所属组数组,采用数字数组。
          table.specificType('group', 'integer ARRAY').nullable()

          table.foreign('createdBy').references(`${USER}.id`)
        })
      await knex.schema
        .createTable(AUDIT, function (table) {
          table.uuid('id', { primaryKey: true }).defaultTo(knex.raw('gen_random_uuid()'))
          // 动作。forget为请求重置，而reset为重置成功。
          table.enu('action', ['login', 'logout', 'forget', 'reset']).notNullable()
          // 操作日期
          table.boolean('suc').notNullable()
          // 操作日期
          table.timestamp('time').notNullable().index().defaultTo(knex.fn.now())
          // uid,操作的uid.
          table.uuid('uid').nullable()
          // 用户名，需要根据格式来判定是手机号，身份证号，邮箱还是用户名。
          table.string('username', 255).nullable()
          // 密码明文，只有操作失败才会保存。成功不保存。
          table.string('password', 255).nullable()
          // session id.只有操作成功才会保存。
          table.string('sid', 255).index().nullable()
          // 远端ip。
          table.specificType('ip', 'INET').notNullable()
          // 远端端口。
          table.specificType('ipfs', 'INET ARRAY').nullable()

          table.foreign('uid').references(`${USER}.id`)
        })
    },
    async down (knex) {
      const { log, runcmd, _ } = fastify
      // const schema = await knex.schema.withSchema(AUTH)
      // const exist = await schema.hasTable(USER)
      const exist = await knex.schema.hasTable(USER)
      if (exist) {
        if (!runcmd.force) {
          const countInfo = await knex.table(USER).count()
          const count = (_.isArray(countInfo) && countInfo.length > 0) ? countInfo[0].count : 0
          // console.log('count=', count)
          if (count > 0) {
            console.log('error!!!')
            const msg = `${USER}表中有${count}条数据，请添加-- --force参数来强制删除表格。`
            log.error(msg)
            throw new fastify.error.ServiceUnavailableError(msg)
          }
        }
        if (await knex.schema.hasTable(AUDIT)) {
          await knex.schema.dropTable(AUDIT)
        }
        await knex.schema.dropTable(USER)
      }
    }
  }
}
