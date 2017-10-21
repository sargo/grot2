module.exports = {
	entry: './src/index.coffee',
  output: {
    filename: 'static/js/grot2.js'
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