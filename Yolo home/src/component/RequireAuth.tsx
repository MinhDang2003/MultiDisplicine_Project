import { Navigate, Outlet , useLocation } from "react-router-dom";

import useAuth from "../hooks/useAuth";

function RequireAuth() {
    const {auth} = useAuth();
    const location = useLocation();
    
    return (
        auth?.token !== "" ? <Outlet/> :
        <Navigate to='/login' state= {{from:location}} replace></Navigate>
    )

}
export default RequireAuth