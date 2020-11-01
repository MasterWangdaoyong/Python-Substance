
# coding: utf-8
import unittest
import logging
log = logging.getLogger(__name__)
import platform
import sys
import os

from pysbs import python_helpers
from pysbs import context
from pysbs import sbsproject, sbsgenerator


testModule = sys.modules[__name__]


class SBSProject_tests(unittest.TestCase):
    SBSPRJFILE = './resources/user_project_{platform}.sbsprj'.format(platform=platform.system().lower())
    SBSPRJFILE_OCIO = './resources/ocio_custom_{platform}.sbsprj'.format(platform=platform.system().lower())
    TOKEN = "\\" if platform.system().lower() == 'windows' else "/"

    def test_ParseSbsPrjFile(self):
        """
        This test checks the parsing of a sbsprj linux file
        """
        sbsPrj = python_helpers.getAbsPathFromModule(testModule, self.SBSPRJFILE)
        aContext = context.Context()
        aProjectMgr = aContext.getProjectMgr()
        aProjectMgr.parseADoc(sbsPrj)
        aSbsPrj = aProjectMgr.getSBSProject()
        self.assertEqual(aSbsPrj.getSettingsInfo().getVersion().getValue(), 2)
        self.assertEqual(aSbsPrj.getProjectInfo().getLabel().getValue(), "User project")
        self.assertEqual(aSbsPrj.getPreferences().getView3d().getStateSaveFileUrl().getValue(), "$(PROJECT_DIR)://user_view3d_settings.sbsscn")
        for workspace in aSbsPrj.getPreferences().getVersionControl().getWorkspaces():
            self.assertEqual(workspace.getWorkspace().getPath().getValue(), "/tmp")
            self.assertEqual(workspace.getSettingsInfo().getVersion().getValue(), 1)
            for inter in workspace.getInterpreters():
                self.assertEqual(inter.getPath().getValue(), "/usr/bin/python2.7")
            actions_label = [action.getLabel().getValue() for action in workspace.getActions()]
            actions_expected = ["Add", "Checkout", "Submit", "Revert", "Get Last Version", "Get Status"]
            self.assertEqual(actions_label, actions_expected)
        for inter in aSbsPrj.getPreferences().getScripting().getInterpreters():
            self.assertEqual(inter.getPath().getValue(), "/home/colin/akm_low_normal-from-mesh.png")
        actions_label = [action.getLabel().getValue() for action in aSbsPrj.getPreferences().getScripting().getActions()]
        actions_expected = ["onBeforeFileLoaded", "onAfterFileLoaded", "onBeforeFileSaved", "onAfterFileSaved", "getGraphExportOptions"]
        self.assertEqual(actions_label, actions_expected)
        self.assertEqual(aSbsPrj.getPreferences().getScenes3d().getSmoothingAngle().getValue(), 180)
        self.assertEqual(aSbsPrj.getPreferences().getSbsTemplates().getDirs()[0].getUrl().getValue(), 'file:///tmp/tmpl')
        self.assertEqual(aSbsPrj.getPreferences().getResources().getUrlAliases()[0].getPath().getValue(), 'file:///tmp/bugcase/A/B/C')
        self.assertEqual(aSbsPrj.getPreferences().getResources().getUrlAliases()[0].getName().getValue(), 'toto')
        self.assertEqual(aSbsPrj.getPreferences().getPython().getPluginPaths()[0].getUrl().getValue(), 'file:///home/colin')
        self.assertEqual(aSbsPrj.getPreferences().getMdl().getIRay().getMdlPaths()[0].getUrl().getValue(), 'file:///home/colin')
        self.assertEqual(aSbsPrj.getPreferences().getLibrary().getWatchedPaths()[0].getUrl().getValue(), 'file:///home/colin')
        self.assertEqual(aSbsPrj.getPreferences().getGeneral().getNormalMapFormat().getValue(), 'directx')
        self.assertEqual(aSbsPrj.getPreferences().getGeneral().getImageOptions().getWebp().getWrite().getWebpQuality().getValue(), 75)
        self.assertEqual(aSbsPrj.getPreferences().getGeneral().getImageOptions().getTga().getWrite().getTgaCompression().getValue(), 'default')
        self.assertEqual(aSbsPrj.getPreferences().getGeneral().getImageOptions().getPng().getWrite().getPngInterlaced().getValue(), False)
        self.assertEqual(aSbsPrj.getPreferences().getGeneral().getImageOptions().getJpg().getWrite().getJpgQuality().getValue(), 75)
        self.assertEqual(aSbsPrj.getPreferences().getGeneral().getImageOptions().getExr().getWrite().getExrLc().getValue(), False)
        self.assertEqual(aSbsPrj.getPreferences().getGeneral().getImageOptions().getBmp().getWrite().getBmpCompression().getValue(), 'default')
        self.assertEqual(aSbsPrj.getPreferences().getGeneral().getDependencies().getPathStorageMethods().getNotNearOrUnder().getValue(), sbsproject.SBSPRJDependenciesPathStorageMethods.ABSOLUTE)
        self.assertEqual(aSbsPrj.getPreferences().getGeneral().getDependencies().getPathStorageMethods().getNearOrUnder().getValue(), sbsproject.SBSPRJDependenciesPathStorageMethods.RELATIVE)
        self.assertEqual(aSbsPrj.getPreferences().getBakers().getNameFilters()[0].getNameFilter()[0].getValue().getValue(), '_low')
        self.assertEqual(aSbsPrj.getPreferences().getBakers().getBakersMacros()[0].getMacros()[0].getKey().getValue(), '$(custom)')
        self.assertEqual(aSbsPrj.getPreferences().getBakers().getBakersMacros()[0].getBakerID().getValue(), 'BakerMeshConverterGLMapBakerManager.AOFromDetail')

    def test_InstanceByContext(self):
        """
        This test checks if the creation through Context's args works fine.
        Use alias test as result.
        :return:
        """
        sbsPrj = python_helpers.getAbsPathFromModule(testModule, self.SBSPRJFILE)
        aProjectMgr = context.ProjectMgr(aSbsPrjFilePath=sbsPrj)
        aProjectMgr.populateUrlAliasesMgr()
        aContext = aProjectMgr.getContext()
        self.assertEqual(aContext.getUrlAliasMgr().mUrlDict, {'sbs': aContext.getDefaultPackagePath(), 'toto': '{0}tmp{0}bugcase{0}A{0}B{0}C'.format(self.TOKEN)})

    def test_ParsePrjFileByGetPrjMgrContext(self):
        """
        This test checks if the getter with prj file parse it correctly.
        Use alias test as result.
        :return:
        """
        sbsPrj = python_helpers.getAbsPathFromModule(testModule, self.SBSPRJFILE)
        aContext = context.Context()
        aProjectMgr = aContext.getProjectMgr(aSbsPrjFile=sbsPrj)
        aProjectMgr.populateUrlAliasesMgr()
        self.assertEqual(aContext.getUrlAliasMgr().mUrlDict, {'sbs': aContext.getDefaultPackagePath(), 'toto': '{0}tmp{0}bugcase{0}A{0}B{0}C'.format(self.TOKEN)})

    def test_PopulateAliasesFromSbsPrj(self):
        """
        This test checks the transfer of sbsprj's alises to pysbs context
        """
        sbsPrj = python_helpers.getAbsPathFromModule(testModule, self.SBSPRJFILE)
        aContext = context.Context()
        aProjectMgr = aContext.getProjectMgr()
        aProjectMgr.parseADoc(sbsPrj)
        aProjectMgr.populateUrlAliasesMgr()
        self.assertEqual(aContext.getUrlAliasMgr().mUrlDict, {'sbs': aContext.getDefaultPackagePath(), 'toto': '{0}tmp{0}bugcase{0}A{0}B{0}C'.format(self.TOKEN)})

    def test_DependenciesPathMethod(self):
        """
        This test checks the shortcut method value of path dependencies method
        """
        sbsPrj = python_helpers.getAbsPathFromModule(testModule, self.SBSPRJFILE)
        aContext = context.Context()
        aProjectMgr = aContext.getProjectMgr()
        self.assertEqual(aProjectMgr.getDependenciesPathStorageMethod(), sbsproject.SBSPRJDependenciesPathStorageMethods.RELATIVE)
        aProjectMgr.parseADoc(sbsPrj)
        self.assertEqual(aProjectMgr.getDependenciesPathStorageMethod(), sbsproject.SBSPRJDependenciesPathStorageMethods.ABSOLUTE)

    def test_SetDependenciesPathMethod(self):
        """
        This test checks the shortcut method value of path dependencies method
        """
        sbsPrj = python_helpers.getAbsPathFromModule(testModule, self.SBSPRJFILE)
        aContext = context.Context()
        aProjectMgr = aContext.getProjectMgr()
        aProjectMgr.setDependenciesPathStorageMethod(sbsproject.SBSPRJDependenciesPathStorageMethods.RELATIVE,
                                                     method=sbsproject.SBSPRJDependenciesPathTypes.NEAR_OR_UNDER)
        aProjectMgr.setDependenciesPathStorageMethod(sbsproject.SBSPRJDependenciesPathStorageMethods.RELATIVE,
                                                     method=sbsproject.SBSPRJDependenciesPathTypes.NOT_NEAR_OR_UNDER)
        self.assertEqual(aProjectMgr.getDependenciesPathStorageMethod(), sbsproject.SBSPRJDependenciesPathStorageMethods.RELATIVE)
        self.assertEqual(aProjectMgr.getDependenciesPathStorageMethod(
            method=sbsproject.SBSPRJDependenciesPathTypes.NEAR_OR_UNDER), sbsproject.SBSPRJDependenciesPathStorageMethods.RELATIVE)
        aProjectMgr.parseADoc(sbsPrj)
        self.assertEqual(aProjectMgr.getDependenciesPathStorageMethod(), sbsproject.SBSPRJDependenciesPathStorageMethods.ABSOLUTE)
        aProjectMgr.setDependenciesPathStorageMethod(sbsproject.SBSPRJDependenciesPathStorageMethods.RELATIVE,
                                                     method=sbsproject.SBSPRJDependenciesPathTypes.NEAR_OR_UNDER)
        self.assertEqual(aProjectMgr.getDependenciesPathStorageMethod(
            method=sbsproject.SBSPRJDependenciesPathTypes.NEAR_OR_UNDER), sbsproject.SBSPRJDependenciesPathStorageMethods.RELATIVE)

    def test_WriteDependenciesPathProjectMgrDriven(self):
        sbsFoo = python_helpers.getAbsPathFromModule(testModule, './resources/A/B/foo.sbs')
        sbsBar = python_helpers.getAbsPathFromModule(testModule, './resources/A/bar.sbs')
        a_ctx = context.Context()
        a_doc = sbsgenerator.createSBSDocument(a_ctx, sbsFoo)
        aPrjMgr = a_ctx.getProjectMgr()
        a_graph = a_doc.createGraph(aGraphIdentifier='test')
        a_graph.createCompInstanceNodeFromPath(a_doc, aPath=sbsBar)
        a_doc.writeDoc()
        with open(sbsFoo, 'r') as f:
            for l in f.readlines():
                l = l.replace("\\", "/") # compat' windows
                self.assertEqual('<filename v="../bar.sbs"/>' in l, True)
        # as absolute
        aPrjMgr.setDependenciesPathStorageMethod(sbsproject.SBSPRJDependenciesPathStorageMethods.ABSOLUTE)
        a_doc = sbsgenerator.createSBSDocument(a_ctx, sbsFoo)
        a_graph = a_doc.createGraph(aGraphIdentifier='test')
        a_graph.createCompInstanceNodeFromPath(a_doc, aPath=sbsBar)
        a_doc.writeDoc()
        with open(sbsFoo, 'r') as f:
            for l in f.readlines():
                l = l.replace("\\", "/") # compat' windows
                self.assertEqual('/resources/A/bar.sbs"/>' in l, True)
        os.remove(sbsFoo)


    def test_ProjectMgrOcioConfigWithPrjFile(self):
        sbsPrj = python_helpers.getAbsPathFromModule(testModule, self.SBSPRJFILE_OCIO)
        ctx = context.Context()
        ocio = ctx.getProjectMgr(sbsPrj).getOcioConfigFilePath()
        self.assertEqual(ocio, "/home/colin/workspace/designer/shared/colormanagement/ocio/substance/config.ocio")


    def test_MultiSbsPrjFiles(self):
        # test with a list of sbsprj
        sbscontext = context.Context()
        sbsPrjOcio = python_helpers.getAbsPathFromModule(testModule, self.SBSPRJFILE_OCIO)
        sbsPrjUser = python_helpers.getAbsPathFromModule(testModule, self.SBSPRJFILE)
        projectmanager = sbscontext.getProjectMgr(aSbsPrjFile=[sbsPrjUser, sbsPrjOcio])
        self.assertEqual(projectmanager.getSBSProject().getPreferences().getColorManagement().getColorManagementEngine().getValue(),
                         "ocio")
        projectmanager.populateUrlAliasesMgr()
        aliasmanager = projectmanager.getUrlAliasMgr()
        self.assertDictEqual(aliasmanager.mUrlDict, {'sbs': context.Context().getDefaultPackagePath(),
                                                     'toto': '{0}tmp{0}bugcase{0}A{0}B{0}C'.format(self.TOKEN),
                                                     'tata': '{0}tmp{0}bugcase{0}A{0}B{0}C'.format(self.TOKEN)})

        # test one after one Sbsprjfiles
        sbscontext = context.Context()
        # user_project.sbsprj
        sbsPrjUser = python_helpers.getAbsPathFromModule(testModule, self.SBSPRJFILE)
        projectmanager = sbscontext.getProjectMgr()
        projectmanager.parseADoc(sbsPrjUser)
        self.assertEqual(
            projectmanager.getSBSProject().getPreferences().getColorManagement().getColorManagementEngine().getValue(),
            "legacy")
        projectmanager.populateUrlAliasesMgr()
        aliasmanager = projectmanager.getUrlAliasMgr()
        self.assertDictEqual(aliasmanager.mUrlDict, {'sbs': context.Context().getDefaultPackagePath(),
                                                     'toto': '{0}tmp{0}bugcase{0}A{0}B{0}C'.format(self.TOKEN)})

        # merge ocio_custom.sbsprj
        sbsPrjOcio = python_helpers.getAbsPathFromModule(testModule, self.SBSPRJFILE_OCIO)
        projectmanager.parseADoc(sbsPrjOcio)
        self.assertEqual(
            projectmanager.getSBSProject().getPreferences().getColorManagement().getColorManagementEngine().getValue(),
            "ocio")
        projectmanager.populateUrlAliasesMgr()
        self.assertDictEqual(aliasmanager.mUrlDict, {'sbs': context.Context().getDefaultPackagePath(),
                                                     'toto': '{0}tmp{0}bugcase{0}A{0}B{0}C'.format(self.TOKEN),
                                                     'tata': '{0}tmp{0}bugcase{0}A{0}B{0}C'.format(self.TOKEN)})

