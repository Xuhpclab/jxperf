package instrumenter;

import org.joda.time.LocalTime;

import org.objectweb.asm.commons.AdviceAdapter;
import java.lang.instrument.ClassFileTransformer;
import java.lang.instrument.Instrumentation;
import java.security.ProtectionDomain;
import org.objectweb.asm.*;

public class LayerInstrumenter {

//     private static class TimeClassFileTransformer implements ClassFileTransformer {
//         @Override
//         public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined, ProtectionDomain protectionDomain, byte[] classfileBuffer) {
//             // if (className.startsWith("java") || className.startsWith("jdk") || className.startsWith("javax") || className.startsWith("sun") || className.startsWith("com/sun")|| className.startsWith("com.google.monitoring.runtime.instrumentation")) {
//             //     //return null或者执行异常会执行原来的字节码
//             //     return null;
//             // }
//             // System.out.println("loaded class: " + className);
//             ClassReader reader = new ClassReader(classfileBuffer);
//             ClassWriter writer = new ClassWriter(reader, ClassWriter.COMPUTE_FRAMES | ClassWriter.COMPUTE_MAXS);
//             reader.accept(new TimeClassVisitor(writer), ClassReader.EXPAND_FRAMES);
//             // return writer.toByteArray();
//             return null;
//         }
//     }

//     public static class TimeClassVisitor extends ClassVisitor {
//         public TimeClassVisitor(ClassVisitor classVisitor) {
//             super(Opcodes.ASM5, classVisitor);
//         }
//         @Override
//         public MethodVisitor visitMethod(int methodAccess, String methodName, String methodDesc, String signature, String[] exceptions) {
//             MethodVisitor methodVisitor = cv.visitMethod(methodAccess, methodName, methodDesc, signature, exceptions);
//             return new TimeAdviceAdapter(Opcodes.ASM5, methodVisitor, methodAccess, methodName, methodDesc);
//         }
//   }

//   public static class TimeAdviceAdapter extends AdviceAdapter {
//         private String methodName;
//         protected TimeAdviceAdapter(int api, MethodVisitor methodVisitor, int methodAccess, String methodName, String methodDesc) {
//             super(api, methodVisitor, methodAccess, methodName, methodDesc);
//             this.methodName = methodName;
//         }
//         @Override
//         protected void onMethodEnter() {
//             //在方法入口处植入
//             if ("<init>".equals(methodName)|| "<clinit>".equals(methodName)) {
//                 return;
//             }
//             mv.visitTypeInsn(NEW, "java/lang/StringBuilder");
//             mv.visitInsn(DUP);
//             mv.visitMethodInsn(INVOKESPECIAL, "java/lang/StringBuilder", "<init>", "()V", false);
//             mv.visitVarInsn(ALOAD, 0);
//             mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/Object", "getClass", "()Ljava/lang/Class;", false);
//             mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/Class", "getName", "()Ljava/lang/String;", false);
//             mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/StringBuilder", "append", "(Ljava/lang/String;)Ljava/lang/StringBuilder;", false);
//             mv.visitLdcInsn(".");
//             mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/StringBuilder", "append", "(Ljava/lang/String;)Ljava/lang/StringBuilder;", false);
//             mv.visitLdcInsn(methodName);
//             mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/StringBuilder", "append", "(Ljava/lang/String;)Ljava/lang/StringBuilder;", false);
//             mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/StringBuilder", "toString", "()Ljava/lang/String;", false);
//             mv.visitMethodInsn(INVOKESTATIC, "instrumenter/LayerCallback", "start", "(Ljava/lang/String;)V", false);
//             mv.visitMethodInsn(INVOKESTATIC, "org.deeplearning4j.nn.multilayer.MultiLayerNetwork", "operatorHook", "(Ljava/lang/String;)V", false);
//       }

//       @Override
//       protected void onMethodExit(int i) {
//             //在方法出口植入
//             if ("<init>".equals(methodName) || "<clinit>".equals(methodName)) {
//                 return;
//             }
//             mv.visitTypeInsn(NEW, "java/lang/StringBuilder");
//             mv.visitInsn(DUP);
//             mv.visitMethodInsn(INVOKESPECIAL, "java/lang/StringBuilder", "<init>", "()V", false);
//             mv.visitVarInsn(ALOAD, 0);
//             mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/Object", "getClass", "()Ljava/lang/Class;", false);
//             mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/Class", "getName", "()Ljava/lang/String;", false);
//             mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/StringBuilder", "append", "(Ljava/lang/String;)Ljava/lang/StringBuilder;", false);
//             mv.visitLdcInsn(".");
//             mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/StringBuilder", "append", "(Ljava/lang/String;)Ljava/lang/StringBuilder;", false);
//             mv.visitLdcInsn(methodName);
//             mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/StringBuilder", "append", "(Ljava/lang/String;)Ljava/lang/StringBuilder;", false);
//             mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/StringBuilder", "toString", "()Ljava/lang/String;", false);
//             mv.visitVarInsn(ASTORE, 1);
//             mv.visitFieldInsn(GETSTATIC, "java/lang/System", "out", "Ljava/io/PrintStream;");
//             mv.visitTypeInsn(NEW, "java/lang/StringBuilder");
//             mv.visitInsn(DUP);
//             mv.visitMethodInsn(INVOKESPECIAL, "java/lang/StringBuilder", "<init>", "()V", false);
//             mv.visitVarInsn(ALOAD, 1);
//             mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/StringBuilder", "append", "(Ljava/lang/String;)Ljava/lang/StringBuilder;", false);
//             mv.visitLdcInsn(": ");
//             mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/StringBuilder", "append", "(Ljava/lang/String;)Ljava/lang/StringBuilder;", false);
//             mv.visitVarInsn(ALOAD, 1);
//             mv.visitMethodInsn(INVOKESTATIC, "instrumenter/LayerCallback", "cost", "(Ljava/lang/String;)J", false);
//             mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/StringBuilder", "append", "(J)Ljava/lang/StringBuilder;", false);
//             mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/StringBuilder", "toString", "()Ljava/lang/String;", false);
//     }
//   }

  //useless rn
  public static void premain(String args, Instrumentation instrumentation) {
    // Cannot get into here, because we don't use javaagent for this jar
    // instrumentation.addTransformer(new TimeClassFileTransformer());
  }

    // public static void main(String[] args) {
    //   LocalTime currentTime = new LocalTime();
	// 	  System.out.println("The current local time is!!!: " + currentTime);
    // }
}
