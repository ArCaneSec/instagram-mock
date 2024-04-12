import Image from "next/image";
import Link from "next/link";
import Timeline from "./client_comps";
import { urls } from "./urls";

export default function Home() {
  return <NavBar />;
}

function NavBar() {
  return (
    <main>
      <nav
        id="menu-tab"
        className="border-r w-1/6 h-dvh bg-slate-950 flex-wrap flex-col text-white font-roboto text-xl py-2"
      >
        <NavBarLogo />
        <NavItem itemName={"Profile"} imageSrc={"profile.svg"} />
        <NavItem itemName={"Timeline"} imageSrc={"timeline.svg"} />
        <NavItem itemName={"Settings"} imageSrc={"setting.svg"} />
        <NavItem itemName={"Logout"} imageSrc={"logout.svg"} />
        {/* <NavBarButton /> */}
      </nav>
      <Timeline />
    </main>
  );
}

function NavItem({ itemName, imageSrc }) {
  return (
    <div className="flex flex-row hover:bg-slate-800 w-full h-10 text-xl gap-1 mt-1 items-center">
      <span className="pl-12">
        <Image
          src={imageSrc}
          alt="profile icon"
          width={20}
          height={20}
          className="dark:invert"
        />
      </span>
      <Link href={urls.profile} className="px-3">
        {itemName}{" "}
      </Link>
    </div>
  );
}

function NavBarLogo() {
  return (
    <div
      id="nav-bar-logo"
      className="flex flex-col items-center border-b font-dancing-script text-3xl pb-2"
    >
      <div>
        <Image
          src="instalogo.svg"
          alt="nav-bar-logo"
          width={50}
          height={50}
          className="dark:invert"
        />
      </div>
      Instagram Moc
    </div>
  );
}

function NavBarButton() {
  return <div className="">close</div>;
}

function Post(post) {
  return (
    <>
      <li key={post.id}></li>
    </>
  );
}
