 var webpack = require('webpack');

 module.exports = {
     entry: './src/index.js',
     output: {
         path: __dirname + '/bin',
         filename: 'bundle.js'
     },
     module: {
        loaders: [{
            test: /\.js$/,
            exclude: /node_modules/,
            loader: 'babel-loader',
            query: {
                presets: ['react', 'es2015'] 
            }
        }]
    },
    plugins: [
        new webpack.DefinePlugin({
            'process.env': {
                'NODE_ENV': JSON.stringify('production')
            }
        }),
        new webpack.optimize.UglifyJsPlugin({
            compressor: {
                warnings: false
            }
        })
    ]
 };
