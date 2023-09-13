'use strict'

module.exports = async function (fastify, opts) {
  const { soa } = fastify
  fastify.get('/',
    async function (request, reply) {
      const env = await soa.get('env')
      if (await env.isDev()) {
        const endPoint = `${request.protocol}://${request.hostname}`
        // reply.redirect(302, `http://localhost:5173/ide/res/index.html#ep=${endPoint}`)
        reply.redirect(302, `https://www.pinyan.tech/ide/res/index.html#ep=${endPoint}`)
        // console.log('endPoint=', endPoint)
      } else {
        return { root: true }
      }
    })
}
