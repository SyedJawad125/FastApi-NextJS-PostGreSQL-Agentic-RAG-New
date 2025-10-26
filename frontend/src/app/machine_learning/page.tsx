'use client'
import React from 'react'
import AdminSideNavbarCom from "@/components/AdminSideNavbarCom";
import Machine_Learning from "@/components/Machine_Learning";


const page = () => {
  return (
    <div className="flex h-screen">
      <div className="w-[16%] bg-gray-800 text-white">
        <AdminSideNavbarCom />
      </div>
      <div className="w-[84%] p-6 bg-black">
      <Machine_Learning/> 
      </div>
    </div> 
  )
}

export default page
