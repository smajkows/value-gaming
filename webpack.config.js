var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');

module.exports = {
  context: __dirname,

  entry: './value_gaming/static/js/index',

  output: {
      path: path.resolve('./value_gaming/static/bundles/'),
      filename: "[name]-[hash].js",
  },

  plugins: [
    new BundleTracker({filename: './value_gaming/webpack-stats.json'}),
  ],

  module: {
    rules: [
      {
          test:/\.css$/,
          use:['style-loader','css-loader']
      },
      {
        test: /\.js$|jsx/,
        exclude: /node_modules/,
        use: ['babel-loader']
      }
    ]
  },
  resolve: {
    extensions: ['*', '.js', '.jsx']
  }

};