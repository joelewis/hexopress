import React from 'react'
import {Link} from 'react-router'
import NavBar from './NavBar'
import Footer from './Footer'

class MainLayout extends React.Component {

    constructor(props) {
        super(props)
    }

    render() {
        console.log(this.props)
        return (
            <div>
                <NavBar/>
                <div className="container grid-960">
                    <div className="columns">
                        <div className="col-2">
                            <ul className="nav">
                                <li className={"nav-item " + (this.props.location.pathname === '/' ? 'active' : '')}>
                                    <Link className="sidebar-link" to="/">Refresh Blog</Link>
                                </li>
                                <li className={"nav-item " + (this.props.location.pathname === '/app/settings/blog' ? 'active' : '')}>
                                    <Link className="sidebar-link" to="/app/settings/blog">Blog Settings</Link>
                                </li>
                                <li className={"nav-item " + (this.props.location.pathname === '/app/settings/account' ? 'active' : '')}>
                                    <Link className="sidebar-link" to="/app/settings/account">Account Settings</Link>
                                </li>
                                <li className={"nav-item " + (this.props.location.pathname === '/app/faq' ? 'active' : '')}>
                                    <Link className="sidebar-link" to="/app/faq">FAQ</Link>
                                </li>
                            </ul>
                        </div>
                        <div className="col-9">
                            {this.props.children}
                        </div>
                    </div>
                </div>
                <Footer/>
            </div>
        )
    }
}

export default MainLayout