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

function setup (fastify) {
  return `
  type Query {
    me: User
  }
  enum Role {
    USER
    ADMIN
  }
  enum Group {
    USER
  }
  type User implements Node {
    id: ID
    role: [Role!]
    group: [Group!]
    name: String
    expires: String
    avatar: String
  }
`
}

module.exports = setup
