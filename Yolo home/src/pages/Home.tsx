import {Link } from "react-router-dom";
import Users from "../component/Users";
import Sidebar from "../component/Sidebar";
function Home() {
	return (
		<div className="flex h-screen w-screen min-h-screen items-start overflow-y-auto">
			<aside className="sticky h-screen left-0 top-0">
				<Sidebar />
			</aside>
			<section className="flex-grow p-6">
				<h1>Dashboard</h1>
				<br />
				<Users />
				<br />
				<div className="flex">
					<Link to="/">Home</Link>
				</div>
			</section>
		</div>
	);
}
export default Home;
