module.exports = {
	entry: {
	  game: './src/index.coffee',
	  match: './src/match.coffee',
	  demo: './src/demo.coffee',
	  login: './src/login.coffee',
	},
  output: {
    filename: 'static/js/[name].js'
  },
  module: {
    rules: [
      {
        test: /\.coffee$/,
        use: [ 'coffee-loader' ]
      }
    ]
  }
}