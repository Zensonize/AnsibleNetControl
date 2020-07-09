const Pool = require('pg').Pool
const pool = new Pool({
    user: 'me',
    host: 'db',
    database: 'ansibru',
    password: 'password',
    port: 5432,
})

module.exports = {
    pool
}