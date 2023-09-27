
const crypto = require('crypto')

module.exports = async function (fastify, opts) {
  const { soa, error, config, util, _ } = fastify
  const cfgutil = config.util
  const passport = await soa.get('passport')
  const auditCfg = cfgutil.dget('passport.audit', {})
  // 允许用户名密码登录的用户名正则。默认为'.*',全部允许。设置为false禁止用户名密码登录。
  const pwdRE = cfgutil.dget('passport.strategies.local.pwdRE', '.*')

  // const fsmInst = await soa.get('fsm')

  // const loginDev = parseInt(cfgutil.dget('passport.strategies.local.loginDev', '1'))
  // fastify.get('/v1/auth/info',
  //   async function (request, reply) {
  //     console.log('fsmInst=', fsmInst.load)
  //     const fsm = await fsmInst.load('user', request)
  //     console.log('fsm=', fsm)
  //     const ret = request.isAuthenticated() ? _.clone(request.user) : {}
  //     console.log('request.session.expires=', request.session)
  //     if (ret.id && request.session.expires) {
  //       ret.expires = request.session.expires
  //     }
  //     console.log('ret=', ret)
  //     return ret
  //   }
  // )

  fastify.post('/auth/login',
    {
      schema: {
        body: {
          $ref: '/v1/auth/login#'
        }
      }
    },
    async function (request, reply) {
      // console.log('123')
      // if (request.isAuthenticated()) {
      //   throw new error.PreconditionRequiredError('Already logined')
      // }
      //, { successRedirect: '/' , failureRedirect: '/login'}
      const Handler = await passport.authenticate('local')
      await Handler(request, reply)
      if (!auditCfg.disabled) {
        const ojs = await soa.get('objection')
        const Audit = ojs.Model.store.audit
        const ipfs = _.drop(util.forwarded(request))
        // 处理loginDev,从审计表中获取uid并且sid不空，销毁sid并且设置退出状态。
        // if (loginDev > 0 && request.isAuthenticated()) {
        //   const rmCount = await Audit.rmLogin({
        //     id: request.user.id,
        //     loginDev,
        //     sessionStore: fastify.sessionStore
        //   }).catch(e => {
        //     log.warn('删除登录信息错误:%s', e)
        //   })
        //   if (rmCount > 0) {
        //     const auditJSON = {
        //       action: 'logout',
        //       suc: true,
        //       uid: request.user.id,
        //       username: request.user.name,
        //       ip: request.ip,
        //       ipfs,
        //       sid: `${rmCount}::uid::${request.user.id}`
        //     }
        //     await Audit.query().insert(auditJSON)
        //   }
        //   // const Sess = await soa.get('session')
        //   // console.log('request.session.store=', Sess)
        // }
        // 添加审计信息。
        const auditJSON = {
          action: 'login',
          suc: false,
          username: request.body.username,
          ip: request.ip,
          ipfs
        }
        // console.log('request.session=', request.session)
        if (request.isAuthenticated()) {
          auditJSON.suc = true
          auditJSON.uid = request.user.id
          auditJSON.sid = request.session.meta().id
        } else {
          auditJSON.password = request.body.password
        }

        // 审计及其后续的通知不干涉当前登录请求．
        Audit.query().insert(auditJSON).then(async insertedAudit => {
          const corsws = await soa.get('corsws')
          let topicSuffx = ''
          if (_.isBoolean(auditJSON.suc)) {
            topicSuffx = auditJSON.suc ? '_1' : '_0'
          }
          const baseTopic = 'audit'
          const topic = `${baseTopic}${topicSuffx}`
          // 反向通道可以不等待其处理完毕．不影响当前request/response.
          corsws.update(baseTopic, { add: insertedAudit })
          corsws.update(topic, { add: insertedAudit })
        })
        // console.log('insertedAudit=', insertedAudit)
      }
      // console.log('request.isAuthenticated', request.isAuthenticated())
      if (request.isAuthenticated()) {
        const ret = _.clone(request.user)
        if (request.body.keep) {
          // 或者使用reply.setcooke?
          const maxDayAge = cfgutil.has('passport.local.keep') ? parseInt(cfgutil.get('passport.local.keep')) : 365
          const maxAge = maxDayAge * 24 * 60 * 60
          const newToken = await request.session.touch(request, reply, maxAge)
          console.log('newToken=', newToken)
          // request.session.regenerate()
          // console.log('request.session=', request.session)
        }
        return { data: ret }
      }
      // return { error: 'unAuthenticated' }
      // return {}
      // return {
      //   ok: false
      // }
      // console.log('after handler')
    })

  fastify.post('/auth/logout',
    async function (request, reply) {
      // console.log('before handler', request.body)
      if (!request.isAuthenticated()) {
        throw new error.UnauthorizedError('not logined')
      }
      const sid = request.session.meta().id
      const name = request.user.name
      const uid = request.user.id

      await request.logout()
      if (!auditCfg.disabled) {
        const ojs = await soa.get('objection')
        const Audit = ojs.Model.store.audit
        const ipfs = _.drop(util.forwarded(request))
        await Audit.logout(sid, {
          uid,
          username: name,
          ip: request.ip,
          ipfs
        })
      }
      return {
        data: {
          id: ''
        }
      }
    }
  )

  fastify.post('/auth/reg',
    async function (request, reply) {
      // console.log('before handler', request.body)
      if (request.isAuthenticated()) {
        throw new error.PreconditionRequiredError('Already logined')
      }
      const username = request.body.username
      const origpwd = request.body.password

      if (pwdRE && !(new RegExp(pwdRE)).test(origpwd)) {
        throw new error.PreconditionRequiredError('password not allowed')
      }

      const password = crypto.createHash('md5').update(origpwd).digest('hex')
      const ojs = await soa.get('objection')
      const Users = ojs.Model.store.users
      const colName = await Users.colName(fastify, username)
      const user = await Users.query()
        .select('*') // 'id', 'accountName', 'nickName', 'commonName', 'email', 'mobile', 'name', 'idcard', 'password', 'avatar', 'role', 'group', 'active', 'ota', 'otaExpire')
        .where(colName, username)
        .limit(2)
      if (user.length > 0) {
        throw new error.PreconditionRequiredError(username + ' Already exists')
      }
      // 默认注册直接激活．不block.
      const newUser = {
        [colName]: username,
        password,
        active: true
      }
      await Users.query().insert(newUser)
      // 开始自动登录
      const Handler = await passport.authenticate('local')
      await Handler(request, reply)

      if (!auditCfg.disabled) {
        const Audit = ojs.Model.store.audit
        const ipfs = _.drop(util.forwarded(request))
        // 添加审计信息,不保存密码原文．
        const auditJSON = {
          action: 'reg',
          suc: false,
          username: request.body.username,
          ip: request.ip,
          ipfs
        }
        // 无需等待其处理完毕．不影响当前request/response.
        Audit.query().insert(auditJSON)
      }
      if (request.isAuthenticated()) {
        const ret = _.clone(request.user)
        return { data: ret }
      }
    }
  )  
}
