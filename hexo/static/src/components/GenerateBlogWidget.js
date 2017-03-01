import React from 'react'

class GenerateBlogWidget extends React.Component {

    render() {
        return (
            <div className="card startblog-card">
                <div className="card-image">
                    {/*<img class="img-responsive" src="img/osx-el-capitan.jpg" title="" style="">*/}
                </div>
                <div className="card-header">
                    <div className="card-title">http://hexopress.com/@lewis.joe.18</div>
                    {/*<div className="card-meta">Software and hardware</div>*/}
                </div>
                <div className="card-body">
                    Looks like you haven't started your blog yet.
                </div>
                <div className="card-footer">
                    <a href="#cards" className="btn btn-primary">Generate blog now</a>
                </div>
            </div>
        )
    }
}

export default GenerateBlogWidget