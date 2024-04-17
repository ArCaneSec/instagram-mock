"use client";
import fetchRequest from "@/app/(authenticated)/utils";
import { apis } from "@/app/urls";
import Image from "next/image";
import { useEffect, useState } from "react";

export default function userPreview({ params }) {
  const [userData, setUserData] = useState({});
  const getData = async () => {
    const res = await fetchRequest(
      `${apis.userData}${params.username}/`,
      "GET"
    );
    if (!res.ok) return <div>User not found</div>;
    setUserData(await res.json());
  };

  useEffect(() => {
    getData();
  }, []);
  return (
    <div className=" gap-5 py-10 mx-96">
      <div>
        <Image
          src={userData.profile ? userData.profile : apis.notFound}
          width={200}
          height={200}
          style={{ borderRadius: "50%" }}
        ></Image>
      </div>
      <UserTextData userData={userData} />
    </div>
  );
}

function UserTextData({ userData }) {
  const eachRowClass = "flex flex-col text-md gap-y-5 text-white";

  return (
    <>
    <div className="flex flex-row gap-5 mx-10">
      <div id="first-row" className={eachRowClass}>
        <span>{userData.userName}</span>
        <span>{userData.totalPosts} posts</span>
      </div>
      <div id="second-row" className={eachRowClass}>
        <span>Followings</span>
        <span>{userData.totalFollowings} Followings</span>
      </div>
      <div id="third-row" className={eachRowClass}>
        <span>Message</span>
        <span>{userData.totalFollowers} Followers</span>
      </div>
    </div>
    <div className="text-white mt-10 ml-10">test</div>
    </>
  );
}
