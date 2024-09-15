$(document).ready(() => {
    $(".itm-hdr_wrpr").click((e) => {
        const header = e.currentTarget;
        const nextElement = header.nextElementSibling;
        const arrowIcon = header.children[1];
        
        $(header).toggleClass("vsbl");
    
        if (header.classList.contains("vsbl")) {
            header.style.borderBottom = "1px solid var(--brdr-color)";
            const itmHght = Math.round(nextElement.children[0].offsetHeight) + 1;
            nextElement.style.height = `${itmHght}px`;
            arrowIcon.style.transform = "rotate(0)";
            
            if (header.parentElement.parentElement.children.length <= 1) {
                $(".sub-itms_wrpr").css("border-bottom", "1px solid var(--brdr-color)");
            }
        } else {
            setTimeout(() => {
                header.style.borderBottom = "unset";
            }, 340);
            nextElement.style.height = "0";
            arrowIcon.style.transform = "rotate(-90deg)";
            
            if (header.parentElement.parentElement.children.length <= 1) {
                $(".sub-itms_wrpr").css("border-bottom", "0");
            }
        }
    });
});