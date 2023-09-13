/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                               //
//                                                                         //
//  WIDE website: http://www.wware.org/                                    //
//  WIDE website: http://www.prodvest.com/                                 //
//  License : WWARE LICENSE(https://www.wware.org/license.html)            //
/// /////////////////////////////////////////////////////////////////////////
// Created On : 21 Sep 2022 By 李竺唐 of SanPolo.Co.LTD
// File: user

const TABLENAME = 'users'
module.exports.setup = async function (fastify, ojs) {
  // console.log('123')
  const { _ } = fastify
  class Users extends ojs.Model {
    static get tableName () {
      return TABLENAME
    }

    static NEXTACTION = {
      Active: 1
    }

    // 处理下一动作。
    async $procAction () {
      // 如果未指定id,则返回错误。
      if (!this.id) {
        return false
      }
      const patch = {}
      if (_.isArray(this.nextAction) && this.nextAction.length > 0) {
        let next = this.nextAction.shift()
        while (next) {
          switch (next) {
            case Users.NEXTACTION.Active:
              patch.active = true
              break
          }
          next = this.nextAction.shift()
        }
      }
      if (!_.isEmpty(patch)) {
        await Users.query().findById(this.id).patch(patch)
      }
      return true
    }

    // @TODO: 需要自动创建及更新schem。以验证数据内容。
    // static get jsonSchema() {}

    $parseDatabaseJson (json) {
      // Remember to call the super class's implementation.
      json = super.$parseDatabaseJson(json)
      // 将role,group默认值改为数组。
      json.role = json.role || []
      json.group = json.group || []
      json.nextAction = json.nextAction || []
      return json
    }

    $formatDatabaseJson (json) {
      // Remember to call the super class's implementation.
      json = super.$formatDatabaseJson(json)
      // 删除role/group.如果是默认值。
      if (_.isArray(json.role) && json.role.length === 0) delete json.role
      if (_.isArray(json.group) && json.group.length === 0) delete json.group
      if (_.isArray(json.nextAction) && json.nextAction.length === 0) delete json.nextAction
      return json
    }
  }
  // console.log('ojs', ojs)
  ojs.Model.store[TABLENAME] = Users
}
