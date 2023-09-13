/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                                 //
//                                                                          //
//  WIDE website: http://www.prodvest.com/                                  //
//  WIDE website: http://www.pinyan.tech/                                   //
//  License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)       //
/// //////////////////////////////////////////////////////////////////////////
// Created On : 24 Dec 2022 By 李竺唐 of 北京飞鹿软件技术研究院
// File: auth

async function setup (fastify) {
  const { _, error, log } = fastify
  // const passport = await soa.get('passport')
  // const cfgutil = config.util
  return {
    Query: {
      me: (parent, args, ctx, arg4) => {
        return ctx.request.isAuthenticated() ? _.clone(ctx.request.user) : {}
      }
    },
    Mutation: {
      login: async (parent, args, ctx, info) => {
        console.log('enter login!')
        const { request } = ctx
        if (request.isAuthenticated()) {
          throw new error.PreconditionRequiredError('Already logined')
        }
        // const Handler = await passport.authenticate('local')
        // await Handler(request, reply)

        log.error('12322')
        if (request.isAuthenticated()) {
          const ret = _.clone(request.user)
          // if (request.body.keep) {
          //   // 或者使用reply.setcooke?
          //   const maxDayAge = cfgutil.has('passport.local.keep') ? parseInt(cfgutil.get('passport.local.keep')) : 365
          //   const maxAge = maxDayAge * 24 * 60 * 60 * 1000
          //   request.session.maxAge = maxAge
          //   request.session.expires = new Date(Date.now() + maxAge)
          //   ret.expires = request.session.cookie.expires = request.session.expires
          //   await request.session.touch()
          //   // request.session.regenerate()
          //   // console.log('request.session=', request.session)
          // }
          // const session = soa.get('session')
          // await session.save()
          return ret
        }
        console.log('arg1=', parent)
        console.log('args=', args)
        console.log('arg3.app=', ctx.app === fastify)
        console.log('arg3=', Object.keys(ctx))
        return {}
      }
    }
  }
}

module.exports = setup
