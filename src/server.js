import express from 'express'
import bodyParser from 'body-parser'
import { graphqlExpress, graphiqlExpress } from 'apollo-server-express'
import { makeExecutableSchema } from 'graphql-tools'
import typeDefs from './typedefs'
import resolvers from './resolvers'


const schema = makeExecutableSchema({ typeDefs, resolvers })

function Server() {
  const server = express()
  server.use(
    '/graphql',
    bodyParser.json(),
    graphqlExpress(request => ({
      schema,
      context: {},
    })),
  )
  server.get('/graphiql', graphiqlExpress({ endpointURL: '/graphql' }))
  return server
}

export default Server
