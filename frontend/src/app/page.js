import Image from "next/image";
import Link from "next/link";
import { urls } from "./urls";

export default function Home() {
  return (
    <main>
      <NavItem itemName={"Profile"} imageSrc={"profile.svg"} />
      <NavItem itemName={"Timeline"} imageSrc={"profile.svg"} />
      <NavItem itemName={"Settings"} imageSrc={"profile.svg"} />
    </main>
  );
}

function NavItem({ itemName, imageSrc }) {
  return (
    <div className="flex flex-row hover:bg-slate-700 w-full text-xl gap-1 items-center">
      <span className="pl-10">
        <Image
          src={imageSrc}
          alt="profile icon"
          width={15}
          height={15}
          className="dark:invert"
        />
      </span>
      <Link href={urls.profile} className="px-5">
        {itemName}
      </Link>
    </div>
  );
}
