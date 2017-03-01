import React from 'react'
import NavBar from './NavBar'
import Footer from './Footer'

const MainLayout = (props) => {
    return (
        <div>
            <NavBar/>
            
            <div className="container grid-960">
                <div className="columns">
                    <div className="col-2">
                        <ul className="nav">
                            <li className="nav-item active">
                                <a href="#">Refresh Blog</a>
                            </li>
                            <li className="nav-item">
                                <a href="#">Blog Settings</a>
                            </li>
                            <li className="nav-item">
                                <a href="#">Account Settings</a>
                            </li>
                        </ul>
                    </div>
                    <div className="col-9">
                        {props.children}
                    </div>
                </div>
            </div>
            <Footer/>
        </div>
    )
}

export default MainLayout