
const GROWTH_QUERIES = {
  inviteInfo: `
    query InviteInfo ($inviteCode: String!) {
      inviteInfo(code: $inviteCode) {
        lastName
        firstName
      }
    }`
}

async function gquery(query, vars, operationName='GenericQuery') {
  const url = window.growthURL || `https://growth.originprotocol.com/`
  const body = JSON.stringify({
    operationName,
    variables: vars ? vars : {},
    query: typeof query === 'string' ? query : JSON.stringify(query)
  })
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: 
  })
  if (res.status !== 200) {
    console.error(`Response HTTP status code ${res.status}`)
    return null
  }
  return await res.json()
}
