module.exports = {
  apps : [{
    name: 'dzpk-auto',
    script: 'index.py',
    instances: 1,
    autorestart: true,
    watch: false,
    // python程序位置
    interpreter: 'C:/Python27/python.exe',
    merge_logs: true,
    output: './logs/out.log',
    error: './logs/error.log',
    log_date_format: 'YYYY-MM-DD HH:mm Z',
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'development'
    },
    env_production: {
      NODE_ENV: 'production'
    }
  }],
};
