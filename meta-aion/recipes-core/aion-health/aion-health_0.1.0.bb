SUMMARY = "AION OS low-overhead local health snapshot"
DESCRIPTION = "One-shot boot health status, no daemon, no cloud or model."
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10"
SRC_URI = "file://aion-health.sh file://aion-health.service"
S = "${WORKDIR}"
inherit systemd
SYSTEMD_SERVICE:${PN} = "aion-health.service"
SYSTEMD_AUTO_ENABLE:${PN} = "enable"
do_install() {
    install -d ${D}${bindir} ${D}${systemd_system_unitdir}
    install -m 0755 ${WORKDIR}/aion-health.sh ${D}${bindir}/aion-health
    install -m 0644 ${WORKDIR}/aion-health.service ${D}${systemd_system_unitdir}/aion-health.service
}
FILES:${PN} += "${systemd_system_unitdir}/aion-health.service"
