 module.exports = {
     entry: './src/index.js',
     output: {
         path: './bin',
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
    }
 };
